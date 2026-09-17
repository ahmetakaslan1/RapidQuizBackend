import urllib.request
import json
import time

BASE_URL = "http://localhost:8000/api"

def make_request(method, endpoint, data=None, headers=None):
    url = BASE_URL + endpoint
    req_headers = {'Content-Type': 'application/json'}
    if headers: req_headers.update(headers)
    
    body = json.dumps(data).encode('utf-8') if data else None
    req = urllib.request.Request(url, data=body, headers=req_headers, method=method)
    
    with urllib.request.urlopen(req) as response:
        return response.getcode(), json.loads(response.read().decode())

def run_tests():
    print("--- RAPID QUIZ API REGRESSION TEST ---")
    
    # 1. Get Categories
    print("\n1. Testing GET /categories/")
    status, categories = make_request("GET", "/categories/")
    assert status == 200, f"Failed with {status}"
    print(f"Success! Found {len(categories)} categories.")
    
    if not categories:
        print("No categories found. Skipping game test.")
        return
        
    cat_id = categories[0]['id']
    cat_name = categories[0]['name']
    
    # 2. Start Game
    print(f"\n2. Testing POST /start-game/ with category '{cat_name}'")
    status, game_data = make_request("POST", "/start-game/", {"category_id": cat_id})
    assert status == 200, f"Failed with {status}"
    token = game_data['token']
    questions = game_data['questions']
    print(f"Success! Received token and {len(questions)} questions.")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Submit Answers
    print("\n3. Testing POST /submit-answer/ for 3 questions")
    for i in range(min(3, len(questions))):
        q_id = questions[i]['id']
        payload = {
            "question_id": q_id,
            "selected_option": "A",
            "islem_yapilan_milisaniye": 1500
        }
        status, ans_data = make_request("POST", "/submit-answer/", payload, headers)
        assert status == 200, f"Failed with {status}"
        print(f"Q{i+1} answered. Current Score: {ans_data['current_score']}")
        
    # 4. Submit Score (Honey Pot)
    print("\n4. Testing POST /submit-score/")
    payload = {
        "username": "AutoTester",
        "website_url": "" 
    }
    status, final_res = make_request("POST", "/submit-score/", payload, headers)
    assert status == 200, f"Failed with {status}"
    print(f"Success! Final score submitted: {final_res['final_score']}")
    
    # 5. Leaderboard filtering
    print(f"\n5. Testing GET /leaderboard/?category_id={cat_id}")
    status, leaderboard = make_request("GET", f"/leaderboard/?category_id={cat_id}")
    assert status == 200, f"Failed with {status}"
    print(f"Success! Found {len(leaderboard)} records in this category.")
    
    print("\n✅ ALL TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    try:
        run_tests()
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
