from flask import Flask, request, render_template, jsonify
from backend import generate_key_with_azure, generate_key_with_ibm, generate_key_with_simulator

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_key', methods=['POST'])
def generate_key():
    data = request.json
    provider = data.get('provider')
    key_type = data.get('key_type')
    
    if provider == 'azure':
        subscription_id = data.get('subscription_id')
        resource_group = data.get('resource_group')
        workspace_name = data.get('workspace_name')
        machine_name = data.get('machine_name')
        location = data.get('location')
        print(f"Provider: {provider}, Key Type: {key_type}, Subscription ID: {subscription_id}, Resource Group: {resource_group}, Workspace Name: {workspace_name}, Machine Name: {machine_name}, Location: {location}")  # Debug statement
        key = generate_key_with_azure(subscription_id, resource_group, workspace_name, machine_name, key_type)
    
    elif provider == 'ibm':
        ibm_api_key = data.get('ibm_api_key')
        ibm_machine_name = data.get('ibm_machine_name')
        print(f"Provider: {provider}, Key Type: {key_type}, IBM API Key: {ibm_api_key}, IBM Machine Name: {ibm_machine_name}")  # Debug statement
        key = generate_key_with_ibm(ibm_api_key, ibm_machine_name, key_type)
    
    elif provider == 'simulator':
        print(f"Provider: {provider}, Key Type: {key_type}")  # Debug statement
        key = generate_key_with_simulator(key_type)
    
    else:
        print("Invalid provider selected")  # Debug statement
        return jsonify({'error': 'Invalid provider'}), 400
    
    print(f"Generated Key: {key}")  # Debug statement
    
    if key_type == 'ssh':
        return jsonify(key)
    else:
        return jsonify({'key': key})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
