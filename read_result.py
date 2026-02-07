import json

with open('amazon_test_result.json', 'r') as f:
    data = json.load(f)

print("=" * 70)
print("AMAZON API TEST RESULT")
print("=" * 70)
print()
print(f"Status: {data.get('status')}")
print(f"Message: {data.get('message')}")
print()

if 'config' in data:
    print("Configuration:")
    for key, value in data['config'].items():
        print(f"  {key}: {value}")
    print()

if 'error' in data and data['error']:
    print("Error Details:")
    if isinstance(data['error'], dict):
        for key, value in data['error'].items():
            if key == 'body':
                print(f"  {key}: {value[:200]}..." if len(str(value)) > 200 else f"  {key}: {value}")
            else:
                print(f"  {key}: {value}")
    else:
        print(f"  {data['error']}")
    print()

if 'product' in data and data['product']:
    print("Product Details:")
    for key, value in data['product'].items():
        print(f"  {key}: {value}")
    print()

if 'solution' in data:
    print("Solution:")
    print(f"  {data['solution']}")
    print()

print("=" * 70)
