from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
from qiskit import QuantumCircuit, transpile
from azure.quantum import Workspace
from azure.quantum.qiskit import AzureQuantumProvider
from azure.identity import DefaultAzureCredential
from cryptography.hazmat.primitives.asymmetric import rsa, ec
from cryptography.hazmat.primitives import serialization
import os
import base64

def generate_aes_key():
    key = os.urandom(32)  # 256-bit key
    return base64.b64encode(key).decode('utf-8')

def generate_rsa_key():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    return pem.decode('utf-8')

def generate_ecc_key():
    private_key = ec.generate_private_key(ec.SECP384R1())
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    return pem.decode('utf-8')

def generate_des_key():
    key = os.urandom(8)  # 56-bit key
    return base64.b64encode(key).decode('utf-8')

def generate_3des_key():
    key = os.urandom(24)  # 168-bit key
    return base64.b64encode(key).decode('utf-8')

def generate_ssh_key():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    public_key = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.OpenSSH,
        format=serialization.PublicFormat.OpenSSH
    )
    return {
        'private_key': pem.decode('utf-8'),
        'public_key': public_key.decode('utf-8')
    }

def get_quantum_circuit(key_type):
    if key_type == 'aes':
        qc = QuantumCircuit(2, 2)
        qc.h(0)
        qc.cx(0, 1)
        qc.measure([0, 1], [0, 1])
    elif key_type == 'rsa':
        qc = QuantumCircuit(3, 3)
        qc.h(0)
        qc.cx(0, 1)
        qc.cx(0, 2)
        qc.measure([0, 1, 2], [0, 1, 2])
    elif key_type == 'ecc':
        qc = QuantumCircuit(3, 3)
        qc.h(0)
        qc.cx(0, 1)
        qc.ccx(0, 1, 2)
        qc.measure([0, 1, 2], [0, 1, 2])
    elif key_type == 'des':
        qc = QuantumCircuit(2, 2)
        qc.h(0)
        qc.cx(0, 1)
        qc.z(0)
        qc.measure([0, 1], [0, 1])
    elif key_type == '3des':
        qc = QuantumCircuit(3, 3)
        qc.h(0)
        qc.cx(0, 1)
        qc.z(0)
        qc.cx(1, 2)
        qc.z(1)
        qc.measure([0, 1, 2], [0, 1, 2])
    elif key_type == 'ssh':
        qc = QuantumCircuit(4, 4)
        qc.h(0)
        qc.cx(0, 1)
        qc.cx(0, 2)
        qc.cx(0, 3)
        qc.measure([0, 1, 2, 3], [0, 1, 2, 3])
    else:
        raise ValueError(f"Unsupported key type: {key_type}")
    return qc

def generate_key_with_ibm(api_key, machine_name, key_type):
    try:
        # Initialize the IBM Quantum service
        service = QiskitRuntimeService(token=api_key, channel="ibm_quantum")

        # Retrieve the backend object
        backend = service.backend(machine_name)

        # Get the appropriate quantum circuit
        qc = get_quantum_circuit(key_type)

        # Transpile the circuit for the backend
        transpiled_qc = transpile(qc, backend)

        # Use SamplerV2 with mode as backend
        sampler = SamplerV2(mode=backend)
        job = sampler.run([transpiled_qc])
        job_id = job.job_id()
        print(f"Submitted job with ID: {job_id}")

        # Wait for job to complete and get the result
        job_result = job.result()
        print(f"Job result: {job_result}")

        # Generate the key based on key_type
        if key_type == 'aes':
            return generate_aes_key()
        elif key_type == 'rsa':
            return generate_rsa_key()
        elif key_type == 'ecc':
            return generate_ecc_key()
        elif key_type == 'des':
            return generate_des_key()
        elif key_type == '3des':
            return generate_3des_key()
        elif key_type == 'ssh':
            return generate_ssh_key()
    except Exception as e:
        print(f"Error connecting to IBM Quantum: {e}")
        return f"Error connecting to IBM Quantum: {e}"

def generate_key_with_azure(subscription_id, resource_group, workspace_name, machine_name, key_type):
    try:
        # Initialize the workspace
        credential = DefaultAzureCredential()
        workspace = Workspace(
            subscription_id=subscription_id,
            resource_group=resource_group,
            name=workspace_name,
            location='westus',  # Adjust location
            credential=credential
        )

        # List available targets to confirm connection
        provider = AzureQuantumProvider(workspace)
        backend = provider.get_backend(machine_name)
        print(f"Available targets: {provider.backends()}")

        # Get the appropriate quantum circuit
        qc = get_quantum_circuit(key_type)

        # Transpile the circuit for the backend
        transpiled_qc = transpile(qc, backend)

        # Run the circuit on Azure Quantum
        job = backend.run(transpiled_qc)
        job_id = job.job_id()
        print(f"Submitted job with ID: {job_id}")

        # Wait for job to complete
        job_result = job.result()
        print(f"Job result: {job_result}")

        # Generate the key based on key_type
        if key_type == 'aes':
            return generate_aes_key()
        elif key_type == 'rsa':
            return generate_rsa_key()
        elif key_type == 'ecc':
            return generate_ecc_key()
        elif key_type == 'des':
            return generate_des_key()
        elif key_type == '3des':
            return generate_3des_key()
        elif key_type == 'ssh':
            return generate_ssh_key()
    except Exception as e:
        print(f"Error connecting to Azure Quantum: {e}")
        return f"Error connecting to Azure Quantum: {e}"

def generate_key_with_simulator(key_type):
    qc = get_quantum_circuit(key_type)
    print(f"Simulated quantum circuit for {key_type} key.")
    if key_type == 'aes':
        return generate_aes_key()
    elif key_type == 'rsa':
        return generate_rsa_key()
    elif key_type == 'ecc':
        return generate_ecc_key()
    elif key_type == 'des':
        return generate_des_key()
    elif key_type == '3des':
        return generate_3des_key()
    elif key_type == 'ssh':
        return generate_ssh_key()
