# team4-server

## github-action 관련
team4-server -> Watoon(프로젝트) -> Watoon(앱) 방식으론 자동으로 배포가 안됨!
team4-server -> Watoon, User..(앱)으로 구성되어있어야 배포가 제대로 됨.

team4-server에서 상단에 settings 탭 - Secrets and variables - Action에서 repository secrets 추가하기

여기서 AWS_ACCESS_KEY_ID와 AWS_SECRET_ACCESS_KEY 추가 필요(실제 배포하는 사람의 것)

이후 .github/workflows/deploy.yml에서 secrets.AWS_ACCESS_KEY_ID_jsh 변수 이름을 secrets에 등록한 변수 이름으로 바꿔주기

+ aws에서 미리 어플리케이션과 환경을 생성한 후, deploy 파일에 application_name과 environment_name을 자신의 것으로 맞춰 기재하기

## 소셜 로그인 관련
api는 accounts/kakao/callback, accounts/google/callback
보내야 하는 정보는 소셜로그인 api와의 통신을 통해 얻은 code, nickname(필수 x)

### 구글
구글 api에서 웹 어플리케이션으로 등록, client id랑 secret 알아내서 github에 secret key로 등록시키기. 이후 workfile에 create .env file쪽에 관련 내용 추가 필요

추가로 "승인된 리디렉션 url"에 사이트/accounts/google/callback 추가해야 함

프론트와 협업 관련 글
https://velog.io/@hnnynh/OAuth-2.0과-Django의-구글-소셜로그인

### 카카오
https://velog.io/@yevini118/Django-allauth-카카오-로그인하기


+ 앱 아이콘 등록 후 비즈앱 전환 해야 이메일 얻기 가능

+ 테스트할때 자신의 컴퓨터 ip를 허용 ip에 놓기