#!/usr/bin/env python3
import argparse
import datetime
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path

import requests
import yaml

# Add modules to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))
from modules import metrics
from modules.rules_validator import get_validator

# Load central configuration
CONFIG_PATH = PROJECT_ROOT / "config/local_models.yaml"
if CONFIG_PATH.exists():
    with open(CONFIG_PATH) as f:
        CONFIG = yaml.safe_load(f)
else:
    print(f"❌ Error: Config file not found at {CONFIG_PATH}")
    print("💡 Make sure config/local_models.yaml exists")
    sys.exit(1)

# Get rules validator
validator = get_validator()

# Ollama configuration (can be overridden with env `OLLAMA_API_BASE`)
OLLAMA_BASE = os.environ.get("OLLAMA_API_BASE", "http://localhost:11434").rstrip("/")

# Max attempts for Ollama-related retries before giving up
MAX_OLLAMA_RETRIES = 3


def ensure_ollama_running(
    auto_start: bool = True, start_cmd=None, wait_seconds: int = 10
) -> bool:
    """Ensure Ollama is running. If not running and auto_start is True, attempt to start it.

    This is a best-effort helper. It attempts to use the `ollama` CLI if available.
    Returns True if Ollama is reachable (check_ollama()), False otherwise.
    """
    if check_ollama():
        return True

    if not auto_start:
        return False

    # If start_cmd not provided, try the default `ollama serve` if available
    if start_cmd is None:
        if shutil.which("ollama") is None:
            print("⚠️ 'ollama' not found in PATH; cannot auto-start Ollama.")
            return False
        start_cmd = ["ollama", "serve"]

    # Ensure logs dir exists
    logs_dir = PROJECT_ROOT / "execution" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = logs_dir / "ollama_serve.log"

    try:
        logfile = open(log_path, "ab")
    except Exception:
        logfile = None

    try:
        print(
            f"🟢 Attempting to start Ollama: {' '.join(start_cmd)} (logs: {log_path})"
        )
        # Start Ollama in a new session so it won't be killed with this process
        proc = subprocess.Popen(
            start_cmd,
            stdout=logfile or subprocess.DEVNULL,
            stderr=logfile or subprocess.DEVNULL,
            cwd=str(PROJECT_ROOT),
            start_new_session=True,
        )
    except Exception as e:
        print(f"❌ Failed to start Ollama process: {e}")
        if logfile:
            logfile.close()
        return False

    # Wait for Ollama to become healthy
    for i in range(wait_seconds):
        if check_ollama():
            if logfile:
                logfile.close()
            print(f"🟢 Ollama became healthy after {i + 1}s")
            return True
        time.sleep(1)

    if logfile:
        logfile.close()

    print(f"⚠️ Ollama did not become healthy within {wait_seconds}s after start attempt")
    return check_ollama()


def _requeue_task_with_backoff(
    task, queue_manager, reason: str, attempts_key: str = "ollama_attempts"
):
    """Requeue the given task with an incremented attempts counter and fail the current processing copy.

    Refactored into helpers to reduce cognitive complexity and improve readability.
    """

    def _mark_processing_failed(task_obj, qm, attempts_count, reason_str, meta):
        try:
            qm.fail_task(
                task_obj["id"],
                f"Ollama failure: {reason_str} (attempt {attempts_count})",
            )
        except Exception:
            print("[Requeue] Warning: could not move current processing file to failed")

        try:
            metrics.log_event(
                task_obj.get("id"),
                "processing_failed",
                f"{reason_str} (attempt {attempts_count})",
                model=(meta.get("model") if isinstance(meta, dict) else ""),
                success=False,
            )
        except Exception:
            print("[Requeue] Warning: failed to log processing failure to metrics")

    def _push_requeue_if_applicable(
        task_obj, qm, attempts_count, reason_str, attempts_k, meta
    ):
        if attempts_count <= MAX_OLLAMA_RETRIES:
            new_meta = dict(meta) if isinstance(meta, dict) else {}
            new_meta[attempts_k] = attempts_count
            new_meta["requeue_reason"] = reason_str
            new_meta["original_task_id"] = (
                task_obj.get("id") if isinstance(task_obj, dict) else None
            )

            new_id = qm.push_task(task_obj["description"], new_meta)
            print(
                f"[Requeue] Task requeued as {new_id} (attempt {attempts_count}/{MAX_OLLAMA_RETRIES})"
            )
            try:
                metrics.log_event(
                    new_id,
                    "requeue",
                    f"attempt {attempts_count}/{MAX_OLLAMA_RETRIES}",
                    model=(new_meta.get("model") if isinstance(new_meta, dict) else ""),
                    success=True,
                )
            except Exception:
                print("[Requeue] Warning: failed to log requeue event to metrics")
            return True
        return False

    def _log_fatal_failure(task_obj, attempts_count, meta):
        try:
            metrics.log_event(
                task_obj.get("id"),
                "fatal_failure",
                f"attempts {attempts_count}",
                model=(meta.get("model") if isinstance(meta, dict) else ""),
                success=False,
            )
        except Exception:
            print("[Requeue] Warning: failed to log fatal failure to metrics")

    try:
        metadata = task.get("metadata", {}) if isinstance(task, dict) else {}
        attempts = metadata.get(attempts_key, 0) if isinstance(metadata, dict) else 0
        attempts += 1

        _mark_processing_failed(task, queue_manager, attempts, reason, metadata)

        if _push_requeue_if_applicable(
            task, queue_manager, attempts, reason, attempts_key, metadata
        ):
            return True

        print(f"[Requeue] Max attempts reached ({attempts}). Not requeuing.")
        _log_fatal_failure(task, attempts, metadata)
        return False
    except Exception as e:
        print(f"[Requeue] Unexpected error while requeuing: {e}")
        return False


# --- Helper Functions ---


def check_ollama():
    """Check if Ollama is running and accessible"""
    try:
        # lightweight probe
        response = requests.get(f"{OLLAMA_BASE}/", timeout=3)
        return response.status_code == 200
    except requests.ConnectionError:
        return False
    except requests.Timeout:
        return False
    except Exception:
        return False


def check_ollama_health(timeout: int = 3):
    """Return (healthy: bool, message: str) describing Ollama availability."""
    try:
        r = requests.get(f"{OLLAMA_BASE}/", timeout=timeout)
        return True, f"reachable (status {r.status_code})"
    except requests.exceptions.RequestException as e:
        return False, str(e)


def attempt_start_ollama(wait: int = 5, cmd: str = None):
    """Best-effort attempt to start Ollama locally.

    - `cmd` defaults to the env `OLLAMA_SERVE_CMD` or `ollama serve`.
    - Returns (started: bool, message: str).
    """
    command = cmd or os.environ.get("OLLAMA_SERVE_CMD", "ollama serve")
    try:
        args = shlex.split(command)
        # Start Ollama in its own session so it doesn't get killed with this process
        proc = subprocess.Popen(
            args,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        try:
            metrics.log_event(
                None,
                "ollama_start_attempt",
                f"cmd={command}, pid={proc.pid}",
                success=True,
            )
        except Exception:
            pass

        # Wait a short time and re-check health
        time.sleep(wait)
        healthy, msg = check_ollama_health()
        if healthy:
            return True, f"started (pid={proc.pid}) and healthy"
        return False, f"started (pid={proc.pid}) but unhealthy: {msg}"
    except FileNotFoundError as e:
        try:
            metrics.log_event(
                None, "ollama_start_attempt", f"cmd_not_found: {command}", success=False
            )
        except Exception:
            pass
        return False, f"command not found: {e}"
    except Exception as e:
        try:
            metrics.log_event(
                None, "ollama_start_attempt", f"exception: {e}", success=False
            )
        except Exception:
            pass
        return False, str(e)


def query_ollama(model: str, prompt: str, timeout: int = 120, gentle: bool = False):
    """
    Query Ollama API with the given model and prompt

    Args:
        model: Model name (e.g., 'qwen2.5-coder:7b-instruct-q5_K_M')
        prompt: The prompt to send to the model
        timeout: Request timeout in seconds
        gentle: If True, unload model immediately after use

    Returns:
        str: Model's response, or None if failed
    """
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "keep_alive": 0 if gentle else 300,  # Unload immediately in gentle mode
    }

    last_error = None
    for attempt in range(1, MAX_OLLAMA_RETRIES + 1):
        try:
            response = requests.post(
                f"{OLLAMA_BASE}/api/generate", json=payload, timeout=timeout
            )

            if response.status_code == 200:
                try:
                    data = response.json()
                    result = data.get("response", "")
                    # Log success metric if available
                    try:
                        metrics.log_event(
                            None,
                            "ollama_success",
                            f"model={model}",
                            model=model,
                            success=True,
                        )
                    except Exception:
                        pass
                    return result.strip()
                except Exception as e:
                    last_error = f"invalid_json: {e}"
                    print(f"❌ Ollama returned invalid JSON: {e}")
            else:
                status = response.status_code
                last_error = f"http_{status}"
                # Retry on 5xx server errors, don't retry on 4xx client errors
                if 500 <= status < 600:
                    print(
                        f"⚠️ Ollama server error {status} (attempt {attempt}/{MAX_OLLAMA_RETRIES})"
                    )
                else:
                    print(f"❌ Ollama HTTP Error: {status} (not retrying)")
                    try:
                        metrics.log_event(
                            None,
                            "ollama_error",
                            f"http_{status}",
                            model=model,
                            success=False,
                        )
                    except Exception:
                        pass
                    return None

        except requests.Timeout:
            last_error = "timeout"
            print(f"⚠️ Ollama timeout on attempt {attempt} ({timeout}s)")
        except requests.ConnectionError:
            last_error = "connection_error"
            print(
                f"⚠️ Cannot connect to Ollama (attempt {attempt}/{MAX_OLLAMA_RETRIES})"
            )
        except Exception as e:
            last_error = f"exception: {e}"
            print(f"⚠️ Ollama request exception on attempt {attempt}: {e}")

        # If we reached here, we will retry unless it was last attempt
        if attempt < MAX_OLLAMA_RETRIES:
            backoff = min(1 * (2 ** (attempt - 1)), 30)
            print(f"[Retry] Waiting {backoff}s before next attempt...")
            try:
                time.sleep(backoff)
            except Exception:
                pass

    # All attempts exhausted
    print(
        f"❌ Ollama failed after {MAX_OLLAMA_RETRIES} attempts. Last error: {last_error}"
    )
    try:
        metrics.log_event(
            None,
            "ollama_failure",
            f"attempts={MAX_OLLAMA_RETRIES},last={last_error}",
            model=model,
            success=False,
        )
    except Exception:
        pass
    return None


# --- Pole Functions ---


def pole_1_goals():
    """Reads priorities."""
    path = Path(CONFIG["paths"]["priorities"])
    if not path.exists():
        return "No priorities file found."
    return path.read_text()


def pole_2_knowledge(task_description=None):
    """
    Pole 2: Knowledge - Reads consolidated knowledge (MANDATORY - Rule 2)

    Args:
        task_description: Optional - للبحث عن معرفة ذات صلة بالمهمة

    Returns:
        str: المعرفة المناسبة أو كل المحتوى
    """
    path = Path(CONFIG["paths"]["consolidated_knowledge"])
    if not path.exists():
        validator.add_to_knowledge(
            {
                "type": "warning",
                "content": "قاعدة المعرفة غير موجودة - تم إنشاؤها",
                "timestamp": datetime.datetime.now().isoformat(),
            }
        )
        return "No consolidated knowledge found."

    full_content = path.read_text()

    # إذا لم يكن هناك وصف للمهمة، أرجع كل المحتوى
    if not task_description or len(task_description.strip()) < 5:
        return full_content

    # بحث بسيط: استخراج الكلمات المفتاحية من وصف المهمة
    keywords = [word.lower() for word in task_description.split()[:10]
                if len(word) > 3]  # كلمات أطول من 3 أحرف

    if not keywords:
        return full_content

    # البحث في الأقسام
    relevant_sections = []
    for section in full_content.split('\n## '):
        section_lower = section.lower()
        # إذا وجدنا كلمتين أو أكثر من المهمة في القسم
        matches = sum(1 for kw in keywords if kw in section_lower)
        if matches >= 2:  # على الأقل كلمتين مطابقتين
            relevant_sections.append('## ' + section)

    # إذا وجدنا أقسام ذات صلة، أرجعها
    if relevant_sections:
        result = '\n\n'.join(relevant_sections)
        print(f"[Knowledge] وُجد {len(relevant_sections)} قسم ذو صلة")
        return result

    # إذا لم نجد شيء، أرجع كل المحتوى (better safe than sorry)
    print("[Knowledge] لم توجد أقسام محددة، إرجاع كل المعرفة")
    return full_content


def pole_3_planning(goals, knowledge, dry_run=False, gentle=False):
    """Generates a plan based on goals and knowledge."""
    role_config = CONFIG["roles"]["planner"]
    prompt = f"""
    You are the PLANNER agent in the 7-Pole System.

    GOALS:
    {goals}

    KNOWLEDGE BASE:
    {knowledge}

    Task: Create a detailed execution plan (workflow) to address the top priority.
    Format your response as a numbered list of shell commands or actions.
    """
    if dry_run:
        print(f"[Dry Run] Querying {role_config['model']} for Plan...")
        return "echo 'Dry Run Plan'"

    plan = query_ollama(role_config["model"], prompt, role_config["timeout"], gentle)
    if plan is None:
        # Signal failure to caller so it can requeue/fail the task
        return None
    return plan


def pole_4_execution(plan, dry_run=False, gentle=False):
    """Executes the plan."""
    role_config = CONFIG["roles"]["executor"]
    # In a real scenario, this would parse the plan and execute commands.
    # For safety, we will just log what would be executed or run safe commands.

    print(f"--- EXECUTION PHASE ({role_config['model']}) ---")
    print(f"Plan to execute:\n{plan}")

    if dry_run:
        print("[Dry Run] Skipping actual execution.")
        return "Execution simulated successfully."

    # If sandbox is enabled in CONFIG, run the plan inside the sandbox runner
    sandbox_cfg = CONFIG.get("sandbox", {})
    if sandbox_cfg.get("enabled", False):
        # Prepare arguments
        timeout = sandbox_cfg.get("timeout", 60)
        cpus = sandbox_cfg.get("cpus", 0.5)
        memory = sandbox_cfg.get("memory", "256m")
        image = sandbox_cfg.get("image", "python:3.11-slim")

        # Write plan to temporary file and invoke sandbox_runner
        import subprocess
        import tempfile

        with tempfile.TemporaryDirectory(prefix="sevenpole_sandbox_") as td:
            script_path = Path(td) / "plan.sh"
            script_path.write_text(plan)
            script_path.chmod(0o755)

            cmd = [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "sandbox_runner.py"),
                "--plan-file",
                str(script_path),
                "--timeout",
                str(timeout),
                "--cpus",
                str(cpus),
                "--memory",
                str(memory),
                "--image",
                str(image),
            ]

            try:
                completed = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    timeout=timeout + 5,
                )
                out = completed.stdout.decode(errors="ignore")
                return out
            except subprocess.TimeoutExpired:
                return "Execution sandbox timed out"
            except Exception as e:
                return f"Execution sandbox error: {e}"

    # Fallback: simulated execution (safe)
    return "Execution completed (Simulated for safety)."


def pole_5_evaluation(execution_log, dry_run=False, gentle=False):
    """Evaluates the execution with standardized metrics."""
    from modules.evaluation_metrics import EvaluationMetrics

    role_config = CONFIG["roles"]["evaluator"]

    # Create metrics evaluator
    evaluator = EvaluationMetrics()

    # Perform standardized evaluation
    evaluator.evaluate_completeness(execution_log, ["completed", "success"])
    evaluator.evaluate_correctness(execution_log, ["error", "failed", "exception"])
    evaluator.evaluate_quality(execution_log)
    evaluator.evaluate_compliance(0)  # Get from rules_validator

    # Generate report
    metrics_report = evaluator.generate_report()
    final_score = evaluator.calculate_final_score()

    prompt = f"""
    You are the EVALUATOR agent.

    EXECUTION LOG:
    {execution_log}

    METRICS ANALYSIS:
    {metrics_report}

    Final Score: {final_score:.2%}

    Task: Provide a brief qualitative evaluation based on the metrics above.
    """
    if dry_run:
        print(f"[Dry Run] Querying {role_config['model']} for Evaluation...")
        return (
            f"Evaluation passed (Dry Run)\n\nScore: {final_score:.2%}\n{metrics_report}"
        )

    llm_evaluation = query_ollama(
        role_config["model"], prompt, role_config["timeout"], gentle
    )

    if llm_evaluation is None:
        # Signal failure to caller so it can requeue/fail the task
        return None

    # Combine metrics and LLM evaluation
    full_report = f"""{metrics_report}

## تقييم LLM:
{llm_evaluation}
"""

    return full_report


def pole_6_documentation(evaluation_report):
    """Saves logs and reports."""
    log_dir = Path(CONFIG["paths"]["logs_dir"])
    log_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"cycle_{timestamp}.md"

    content = f"""# Cycle Report {timestamp}

    ## Evaluation
    {evaluation_report}
    """
    log_file.write_text(content)
    print(f"Documentation saved to {log_file}")


def pole_7_decision(evaluation_report, dry_run=False, gentle=False):
    """Decides next steps."""
    role_config = CONFIG["roles"]["decision_maker"]
    prompt = f"""
    You are the DECISION MAKER.

    EVALUATION:
    {evaluation_report}

    Task: Decide the next step. (e.g., 'Continue to next task', 'Retry', 'Ask User').
    """
    if dry_run:
        print(f"[Dry Run] Querying {role_config['model']} for Decision...")
        return "Continue (Dry Run)"

    decision = query_ollama(
        role_config["model"], prompt, role_config["timeout"], gentle
    )
    if decision is None:
        return None
    return decision


# --- Main Cycle ---


def run_cycle(dry_run=False, gentle=False):
    from modules import metrics, queue_manager

    print("--- Starting 7-Pole Cycle (Smart Mode) ---")

    # Check Ollama availability (skip in dry-run mode)
    if not dry_run:
        healthy, msg = check_ollama_health()
        if not healthy:
            auto_start = CONFIG.get("ollama", {}).get("auto_start", True)
            if auto_start:
                print("⚙️ Ollama appears down — attempting auto-start (best-effort)...")
                started, start_msg = attempt_start_ollama(
                    wait=CONFIG.get("ollama", {}).get("wait_seconds", 5),
                    cmd=CONFIG.get("ollama", {}).get("serve_cmd", None),
                )
                if started:
                    print(f"🟢 Ollama auto-start succeeded: {start_msg}")
                    healthy, msg = check_ollama_health()
                else:
                    print(f"⚠️ Ollama auto-start attempt failed: {start_msg}")

            if not healthy:
                print("❌ Error: Ollama is not running or unreachable!")
                print(f"💡 Health check: {msg}")
                print("💡 Start Ollama with: ollama serve")
                print("💡 Or use --dry-run flag for testing without Ollama")
                return

    if gentle:
        print("[Gentle Mode] Models will be unloaded after use. Delays added.")

    # Initialize Metrics
    tracker = metrics.MetricsTracker()

    # 1. Goals (Queue Management)
    tracker.start_pole("goals")
    task = queue_manager.pop_task()
    if not task:
        # If no task in queue, check PRIORITIES.md and push one (Simplified logic)
        raw_goals = pole_1_goals()
        if "Implement" in raw_goals:  # Very simple check
            queue_manager.push_task(
                "Process Priorities File", {"source": "PRIORITIES.md"}
            )
            task = queue_manager.pop_task()

        if not task:
            print("No tasks in queue or priorities. Exiting.")
            return

    print(f"1. Goal Acquired: {task['description']}")
    tracker.end_pole("goals", task["id"], "system")

    # 2. Knowledge
    tracker.start_pole("knowledge")
    knowledge = pole_2_knowledge()
    print(f"2. Knowledge Loaded ({len(knowledge)} chars)")
    tracker.end_pole("knowledge", task["id"], "system")

    # 3. Planning
    tracker.start_pole("planning")
    plan = pole_3_planning(task["description"], knowledge, dry_run, gentle)
    if plan is None and not dry_run:
        # Ollama failed during planning — requeue the task with backoff
        print("[Error] Ollama failed to generate a plan. Attempting to requeue task...")
        _requeue_task_with_backoff(task, queue_manager, "planning_ollama_failure")
        return
    print("3. Plan Generated")
    tracker.end_pole("planning", task["id"], CONFIG["roles"]["planner"]["model"])
    if gentle:
        time.sleep(2)

    # 4. Execution
    tracker.start_pole("execution")
    exec_log = pole_4_execution(plan, dry_run, gentle)
    print("4. Execution Completed")
    tracker.end_pole("execution", task["id"], CONFIG["roles"]["executor"]["model"])
    if gentle:
        time.sleep(2)

    # 5. Evaluation
    tracker.start_pole("evaluation")
    eval_report = pole_5_evaluation(exec_log, dry_run, gentle)
    if eval_report is None and not dry_run:
        print("[Error] Ollama failed during evaluation. Attempting to requeue task...")
        _requeue_task_with_backoff(task, queue_manager, "evaluation_ollama_failure")
        return
    print("5. Evaluation Completed")
    tracker.end_pole("evaluation", task["id"], CONFIG["roles"]["evaluator"]["model"])
    if gentle:
        time.sleep(2)

    # 6. Documentation
    tracker.start_pole("documentation")
    pole_6_documentation(eval_report)
    print("6. Documentation Saved")
    tracker.end_pole("documentation", task["id"], "system")

    # 7. Decision
    tracker.start_pole("decision")
    decision = pole_7_decision(eval_report, dry_run, gentle)
    if decision is None and not dry_run:
        print("[Error] Ollama failed to make a decision. Attempting to requeue task...")
        _requeue_task_with_backoff(task, queue_manager, "decision_ollama_failure")
        return
    print(f"7. Decision: {decision}")
    tracker.end_pole("decision", task["id"], CONFIG["roles"]["decision_maker"]["model"])

    # Complete Task
    queue_manager.complete_task(task["id"], {"decision": decision})
    print("--- Cycle Complete ---")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run 7-Pole System Agent")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without executing external commands or expensive model calls",
    )
    parser.add_argument(
        "--gentle",
        action="store_true",
        help="Conserve resources by unloading models and adding delays",
    )
    args = parser.parse_args()

    # Ensure modules can be imported
    sys.path.append(str(Path(__file__).parent.parent))

    run_cycle(dry_run=args.dry_run, gentle=args.gentle)
