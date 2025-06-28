
# 예약 전략 방법
1. 가장 정상적인 방법 : 9시까지 기다렸다가 DoM API 조작으로 예약 시작. (번거로움/안전함)

2. 로그인 후 TimeRange의 범위를 모두 post 요청한다. -> 테스트 필요/바뀔 가능성 엄청 높음(단순함/IP차단위험)


9시에 새로고침해야함 


# 에러
1. 에러 후  캘린더 클릭 리커버리


# 서버시간 이용
https://time.navyism.com/?host=www.incheoncc.com

# 상세화면 에러
/html/body/div[1]/div[3]/div[2]/div[2]/div/div[3]/div[2]/div/div[2]/div
```
<div id="input_ajax">ERROR : 예약정보가 없습니다.</div>

									<caption>그린피</caption>
									<colgroup>
										<col style="width:25%;">
										<col>
									</colgroup>
									<tbody>
									<tr>
										<th scope="row">그린피</th>
										<td>76,000</td>
									</tr>
									</tbody>
									</table>


									<hr style="border:none; border-top:1px solid #999;">

									<div class="cm_text_center" style="margin:18px 0 0 0;">
										<button style="padding: .5em 3.5em;" class="cm_btn default" type="button" onclick="Javascript:golfsubcmd('R')">
											예약
										</button>
										<button style="padding: .5em 3.5em;" class="cm_btn gray" type="button" onclick="Javascript:golfpagereset('modalPop1');">취소</button>
									</div>	
								</form>
								</div>
								<!-- /예약시간 박스 -->
</div>
```

# 추가 기능 
1. 테스트 모드(실제 예약되지 않음)

