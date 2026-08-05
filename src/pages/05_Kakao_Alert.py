import os
import json
import requests
import streamlit as st

# ==========================================
# 1. 카카오 디벨로퍼스 설정 정보
# ==========================================
# 실제 서비스 시 st.secrets 또는 환경변수로 관리하는 것을 권장합니다.
KAKAO_REST_API_KEY = st.secrets.get("KAKAO_REST_API_KEY", "YOUR_REST_API_KEY_HERE")
REDIRECT_URI = st.secrets.get("REDIRECT_URI", "https://3teamproj.streamlit.app")

# ==========================================
# 2. 카카오톡 API 연동 핵심 함수
# ==========================================

def get_kakao_auth_url():
    """
    카카오 로그인 및 메시지 전송 권한(talk_message) 요청 URL 생성
    """
    auth_url = (
        f"https://kauth.kakao.com/oauth/authorize?"
        f"client_id={KAKAO_REST_API_KEY}&"
        f"redirect_uri={REDIRECT_URI}&"
        f"response_type=code&"
        f"scope=talk_message"
    )
    return auth_url


def get_kakao_access_token(auth_code):
    """
    인가 코드(Authorization Code)로 Access Token 발급 받기
    """
    token_url = "https://kauth.kakao.com/oauth/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded;charset=utf-8"
    }
    data = {
        "grant_type": "authorization_code",
        "client_id": KAKAO_REST_API_KEY,
        "redirect_uri": REDIRECT_URI,
        "code": auth_code
    }

    response = requests.post(token_url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        st.error(f"토큰 발급 실패: {response.text}")
        return None


def send_pill_reminder_to_me(access_token, user_name, time_slot_label, pill_list):
    """
    카카오톡 '나에게 보내기' API를 호출하여 영양제 복용 알림 전송
    """
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # 영양제 목록 텍스트 가공
    pills_text = "\n".join([f"• {pill['name']} ({pill['dosage']})" for pill in pill_list])

    # 카카오톡 메시지 템플릿 (Text 타입)
    template_object = {
        "object_type": "text",
        "text": f"[NutriMatch] {time_slot_label} 영양제 섭취 시간입니다! 💊\n\n"
                f"안녕하세요 {user_name}님!\n"
                f"지금 드셔야 할 영양제 목록입니다:\n\n"
                f"{pills_text}\n\n"
                f"잊지 말고 섭취한 뒤 복용 완료 체크를 해주세요! ✨",
        "link": {
            "web_url": REDIRECT_URI,
            "mobile_web_url": REDIRECT_URI
        },
        "button_title": "💊 나의 약통에서 복용 체크하기"
    }

    payload = {
        "template_object": json.dumps(template_object, ensure_ascii=False)
    }

    response = requests.post(url, headers=headers, data=payload)
    return response.json()


# ==========================================
# 3. Streamlit UI 연동 연동 예시
# ==========================================

def render_kakao_notification_setting():
    """
    나의 약통 페이지 내 카카오톡 알림 연동 세팅 컴포넌트
    """
    st.subheader("💬 카카오톡 복용 알림 연동")

    # 1. URL Parameter에서 Kakao 인가코드 수신 여부 확인
    query_params = st.query_params
    auth_code = query_params.get("code")

    if auth_code and "kakao_access_token" not in st.session_state:
        with st.spinner("카카오톡 연동 승인 중..."):
            token = get_kakao_access_token(auth_code)
            if token:
                st.session_state["kakao_access_token"] = token
                st.success("✅ 카카오톡 알림 연동이 성공적으로 완료되었습니다!")

    # 2. 연동 상태에 따른 UI 표현
    if "kakao_access_token" in st.session_state:
        st.info("🟢 카카오톡 메시지 전송 권한이 연결되어 있습니다.")
        
        # 테스트 발송용 샘플 데이터
        sample_pills = [
            {"name": "락토핏 생유산균 골드", "dosage": "1일 1회 1포"},
            {"name": "L-아르기닌 1000", "dosage": "1일 1회 1정"}
        ]

        if st.button("🚀 카카오톡 알림 테스트 메시지 전송"):
            token = st.session_state["kakao_access_token"]
            result = send_pill_reminder_to_me(token, "홍길동", "🌅 아침 공복", sample_pills)
            
            if result.get("result_code") == 0:
                st.balloons()
                st.success("카카오톡으로 알림 메시지가 성공적으로 발송되었습니다!")
            else:
                st.error(f"메시지 발송 실패: {result}")
    else:
        st.write("설정하신 시간대(아침 공복, 식후, 취침 전)에 맞춰 카카오톡으로 복용 알림을 받아보세요.")
        auth_url = get_kakao_auth_url()
        st.markdown(
            f'<a href="{auth_url}" target="_self">'
            f'<button style="background-color:#FEE500; color:#000000; border:none; padding:10px 20px; font-weight:bold; border-radius:8px; cursor:pointer;">'
            f'💬 카카오톡 알림 연동 시작하기</button></a>',
            unsafe_allow_html=True
        )


if __name__ == "__main__":
    st.title("💊 NutriMatch - 나의 약통")
    render_kakao_notification_setting()
