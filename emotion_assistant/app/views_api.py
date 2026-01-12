from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Patient, Prescription, Snapshot
from .serializers import PatientSerializer, PrescriptionSerializer, SnapshotSerializer

# ✅ Get/POST all patients
@api_view(['GET', 'POST'])
def patients_list(request):
    if request.method == 'GET':
        patients = Patient.objects.all()
        serializer = PatientSerializer(patients, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = PatientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

# ✅ Get/PUT/DELETE a single patient
@api_view(['GET', 'PUT', 'DELETE'])
def patient_detail(request, pk):
    try:
        patient = Patient.objects.get(pk=pk)
    except Patient.DoesNotExist:
        return Response({'error': 'Patient not found'}, status=404)

    if request.method == 'GET':
        serializer = PatientSerializer(patient)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = PatientSerializer(patient, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    elif request.method == 'DELETE':
        patient.delete()
        return Response({'message': 'Patient deleted successfully'})

from .models import Patient, Prescription, Snapshot
from .serializers import PatientSerializer, PrescriptionSerializer, SnapshotSerializer

# ✅ PRESCRIPTION LIST + CREATE
@api_view(['GET', 'POST'])
def prescriptions_list(request):
    if request.method == 'GET':
        prescriptions = Prescription.objects.all()
        serializer = PrescriptionSerializer(prescriptions, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = PrescriptionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

# ✅ PRESCRIPTION DETAILS (GET, UPDATE, DELETE)
@api_view(['GET', 'PUT', 'DELETE'])
def prescription_detail(request, pk):
    try:
        prescription = Prescription.objects.get(pk=pk)
    except Prescription.DoesNotExist:
        return Response({'error': 'Prescription not found'}, status=404)

    if request.method == 'GET':
        serializer = PrescriptionSerializer(prescription)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = PrescriptionSerializer(prescription, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    elif request.method == 'DELETE':
        prescription.delete()
        return Response({'message': 'Prescription deleted successfully'})


# ✅ SNAPSHOT LIST + CREATE
@api_view(['GET', 'POST'])
def snapshots_list(request):
    if request.method == 'GET':
        snapshots = Snapshot.objects.all()
        serializer = SnapshotSerializer(snapshots, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = SnapshotSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

# ✅ SNAPSHOT DETAILS (GET, UPDATE, DELETE)
@api_view(['GET', 'PUT', 'DELETE'])
def snapshot_detail(request, pk):
    try:
        snapshot = Snapshot.objects.get(pk=pk)
    except Snapshot.DoesNotExist:
        return Response({'error': 'Snapshot not found'}, status=404)

    if request.method == 'GET':
        serializer = SnapshotSerializer(snapshot)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = SnapshotSerializer(snapshot, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    elif request.method == 'DELETE':
        snapshot.delete()
        return Response({'message': 'Snapshot deleted successfully'})
