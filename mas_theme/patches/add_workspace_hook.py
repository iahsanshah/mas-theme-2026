import frappe

def execute():
	"""Add workspace_data hook to hooks.py if not present"""
	hooks_file = frappe.get_app_path('mas_theme', 'hooks.py')
	with open(hooks_file, 'r') as f:
		content = f.read()

	if 'workspace_data' not in content:
		with open(hooks_file, 'a') as f:
			f.write('\n# Workspace Data\n# -------------\nworkspace_data = ["config/my_workspace.json"]\n')
