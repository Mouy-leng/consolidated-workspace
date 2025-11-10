from typer.testing import CliRunner
from head_cli import app

runner = CliRunner()

def test_inspect_logs_no_workflow_id():
    result = runner.invoke(app, ["genx", "inspect-logs"])
    assert result.exit_code == 0
    assert "Inspecting CI/CD logs..." in result.stdout
    assert "GitLab CI/CD" in result.stdout
    assert "Simulated GitLab Runner Log Output" in result.stdout
    assert "GitHub Actions" in result.stdout
    assert "--workflow-run-id not provided" in result.stdout

def test_inspect_logs_with_workflow_id():
    result = runner.invoke(app, ["genx", "inspect-logs", "--workflow-run-id", "12345"])
    assert result.exit_code == 0
    assert "Inspecting CI/CD logs..." in result.stdout
    assert "GitLab CI/CD" in result.stdout
    assert "Simulated GitLab Runner Log Output" in result.stdout
    assert "GitHub Actions" in result.stdout
    assert "GitHub Actions log for run 12345" in result.stdout
    assert "Simulated GitHub Actions Log Output for run 12345" in result.stdout

if __name__ == "__main__":
    # This part is for manual testing if needed
    # You can run this script directly to see the output
    print("--- Testing without workflow-run-id ---")
    test_inspect_logs_no_workflow_id()
    print("\n--- Testing with workflow-run-id ---")
    test_inspect_logs_with_workflow_id()
    print("\n--- Raw output for no workflow id ---")
    result = runner.invoke(app, ["genx", "inspect-logs"])
    print(result.stdout)
    print("\n--- Raw output for with workflow id ---")
    result = runner.invoke(app, ["genx", "inspect-logs", "--workflow-run-id", "12345"])
    print(result.stdout)
