
# 예약 전략 방법
1. 가장 정상적인 방법 : 9시까지 기다렸다가 DoM API 조작으로 예약 시작. (번거로움/안전함)

2. 로그인 후 TimeRange의 범위를 모두 post 요청한다. -> 테스트 필요/바뀔 가능성 엄청 높음(단순함/IP차단위험)



9시에 새로고침해야함 


# 에러
1. 에러 후  캘린더 클릭 리커버리


# 서버시간 이용
https://time.navyism.com/?host=www.incheoncc.com

# 에러시 엘리먼트 처리
/html/body/div[1]/div[3]/div[2]/div[2]/div/div[3]/div[2]/div/div[2]/div
<div id="input_ajax">ERROR : 예약정보가 없습니다.</div>

# 정상시 input_ajax 엘리먼트
```
<div id="input_ajax">
<script language="JavaScript" type="text/JavaScript">
<!--

	/*##############################################################################################*/
	//------------------------------------------------------------
	// 
	//------------------------------------------------------------
	function golfsubcmd(atype){

		//alert(atype)
		// 처리
		var actionurl = "/GolfRes/onepage/real_resok.asp";

		// 호출한 값을 알아 온다
		var cmd = $("#golf_cmd").val();
		// 
		if (cmd == "ins"){
			//
			var checkPersonalFalg = golfscheckPersonalForm();

			if(checkPersonalFalg == true ){
				// 입력데이터 가공처리
			

				// 데이터 처리				
				golfsubaction(cmd, actionurl);
			}else{
				if (checkPersonalFalg){
					//
				}else if (checkPersonalFalg=="M"){ 
					//
				
					timeapply_view();
				
				}else{
					//
				
					golfpagereset('modalPop1');
				
				}
			}
		}
	}

	// AJAX 실제 전송.
	function golfsubaction(cmd, actionurl){
			
		var tt = 0;
		// 처리부분	
		if (tt == 1){
			$("#golfdataform").attr("action", actionurl);
			$("#golfdataform").submit();
		}else{
			
			$.ajax({
				async: false,
				type: "POST",
				url : actionurl,
				data : $("#golfdataform").serialize(),
				dataType : "json",
				success:function(success){
					if(success.result == "OK"){
						// 성공처리	
						//alert(unescape(success.gomsg));
						document.location.href = "/GolfRes/onepage/my_golfreslist.asp";
						
						//alert(unescape(success.gomsg));
					} else if ( success.result == "LOGIN"){
						// 로그인 처리
						alert(unescape(success.gomsg));
						document.location.href = unescape(success.gonexturl);
						
					} else if ( success.result == "erUrl"){
						// 로그인 처리
						alert(unescape(success.gomsg));
						document.location.href = unescape(success.gonexturl);
					} else {
						// 에러처리
						alert(unescape(success.gomsg));

					
						golfpagereset('modalPop1')
						//timeapply_view();
					
					}
				},
				error: function(xhr, option, error){
					alert(xhr.status+" | "+error); //오류코드 | 오류내용
				
					golfpagereset('modalPop1');
					//timeapply_view();
				
				}
				/*error : function(success){
					meg = "서버와 통신중 에러가 발생하였습니다."
					alert("처리결과 : "+meg);
				}*/
			});
			// 한글 깨짐 방지 복구처리
		}
		
	}

	// 입력값 체크
	function golfscheckPersonalForm(){

		// 날짜	
		var pointdate = "20250710";
		pointdate = pointdate.substring(0,4)+"-"+pointdate.substring(4,6)+"-"+pointdate.substring(6,8);
		// 시간
		var pointtime = "0518";
		pointtime = pointtime.substring(0,2)+":"+pointtime.substring(2,4);
		// 코스
		var pointname = "IN";

		var toDay = "20250620";
		today  = new Date(toDay.substr(0,4), toDay.substr(4,2), toDay.substr(6,2));
		var newday = new Date(pointdate.substr(0,4), pointdate.substr(4,2), pointdate.substr(6,2));

		if( today > newday) {
			alert('당일예약은 하실수 없습니다. 예약을 원하시면 예약실로 문의해주세요');
			return false;
		}

		// 셀프타이틀
		var self_title = ""

	
			//
//			if(($("#hand_tel1").val().length < 1) || ($("#hand_tel2").val().length < 3) || ($("#hand_tel3").val().length < 3) ){
//				alert("긴급연락처를 정확히 입력후 신청버튼을 클릭하여주십시요.\n회원정보에 등록해 놓으시면 차후 로그인시부터 적용되어 편리하게 이용할 수 있습니다.")
//				$("#hand_tel2").focus();
//				return "M";
//			}
		
		//
//		if(($("#hand_tel1").val().length < 1) || ($("#hand_tel2").val().length < 3) || ($("#hand_tel3").val().length < 3) ){
//			alert("긴급연락처를 정확히 입력후 신청버튼을 클릭하여주십시요.\n회원정보에 등록해 놓으시면 차후 로그인시부터 적용되어 편리하게 이용할 수 있습니다.")
//			$("#hand_tel2").focus();
//			return "M";
//		}
	

		//
		if(confirm(pointdate+"일자 "+pointname+"코스 "+pointtime+" 타임을 예약하시겠습니까?\n"+self_title+"예약이 확정되면 문자로 예약내역이 발송됩니다.")){
		//if(confirm("시간변경은 예약조회/취소 메뉴에서 해당일에 한해 자유롭게 하실수 있으며, 예약취소는 예약일을 제외한 5일전 17:00이전까지 하셔야 위약규정이 적용되지 않습니다.\n ===============================================\n\n"+pointdate+"일자 "+pointname+"코스 "+pointtime+" 타임을 예약하시겠습니까?")){
			return true;
		}else{
			return "M";
		}
	}




/*##############################################################################################*/
//자동실행 - body onload의 대체
$(function(){

});

//-->
</script>



								<h4 class="h4_tit">예약시간</h4>
							
								<!--//예약공지추가-->
								<div class="cm_time_notice">
									<strong>※ 알려드립니다.</strong>
									당 클럽에서는 TEE-OFF 시간을 준수하고 있습니다.<br>
									원활한 경기진행을 위해 <em>30분전 내장, 10분전 라운드</em>를 준비해 주시기 바랍니다.<br><br>
									예약취소는 5일전 18:00 이전까지 취소가 가능합니다. 이후 취소는 예약실로 문의 바랍니다.<br> &lt;9홀&gt; 첫팀 2인 티업 가능합니다. 전화상으로만 예약되오니 문의주시기 바랍니다.(예약실:032-562-9991~2)
								</div>
								<!--예약공지추가//-->

								<!-- 예약시간 박스 -->
								<div class="cm_time_list">

								<form id="golfdataform" name="golfdataform" method="POST">
									<input type="hidden" id="golf_cmd" name="cmd" value="ins">
									<input type="hidden" id="golf_cmval" name="cmval" value="0">	
									<input type="hidden" id="golf_cmkind" name="cmkind" value="">
									<input type="hidden" id="golf_cmrtype" name="cmrtype" value="N">	
									<input type="hidden" id="golf_calltype" name="calltype" value="AJAX">
									<input type="hidden" id="golf_gonexturl" name="gonexturl" value="/GolfRes/onepage/my_golfreslist.asp">
									<input type="hidden" id="golf_backurl" name="backurl" value="">
									<input type="hidden" id="golf_pointdate" name="pointdate" value="20250710">
									<input type="hidden" id="golf_openyn" name="openyn" value="1">
									<input type="hidden" id="golf_dategbn" name="dategbn" value="5">
									<input type="hidden" id="golf_pointid" name="pointid" value="2">
									<input type="hidden" id="golf_pointtime" name="pointtime" value="0518">
									
									<input type="hidden" id="golf_flagtype" name="flagtype" value="I">
									<input type="hidden" id="golf_punish_cd" name="punish_cd" value="UNABLE">
									<input type="hidden" id="apply_self_r_yn" name="self_r_yn" value="N">	
									<input type="hidden" id="golf_res_gubun" name="res_gubun" value="N">
									<input type="hidden" id="golf_virtual_tf" name="virtual_tf" value="">
									
									<input type="hidden" id="golf_coupon_info" name="coupon_info">
									
									<input type="hidden" id="golf_oldpointtime" name="oldpointtime" value="">
									<input type="hidden" id="golf_oldpointid" name="oldpointid" value="">
									<input type="hidden" id="golf_usrmemcd" name="usrmemcd" value="12">
									<input type="hidden" id="golf_memberno" name="memberno" value="12061000">	
									<input type="hidden" id="golf_bookgseq" name="bookgseq" value="">
									<input type="hidden" id="golf_oldhane_tel" name="oldhane_tel" value="">
									
									<input type="hidden" id="golf_column_cpon_code" name="column_cpon_code" value="">
									
									<input type="hidden" id="ref_bigo" name="ref_bigo" value="">

									<table class="cm_time_info_tbl" summary="예약정보를  알려드립니다">
									<caption>예약정보</caption>
									<colgroup>
										<col style="width:25%;">
										<col>
									</colgroup>
									<tbody>
									<tr>
										<th scope="row">신청자</th>
										<td>
								정성호
										</td>
									</tr>
									<tr>
										<th scope="row">핸드폰</th>
										<td>
								
											<input type="hidden" name="hand_tel1" id="hand_tel1" value="010">
											<input type="hidden" name="hand_tel2" id="hand_tel2" value="7430">
											<input type="hidden" name="hand_tel3" id="hand_tel3" value="0955">
											010 - 7430 - 0955
										</td>
									</tr>
									<tr>
										<th scope="row">예약일자</th>
										<td class="emp01">
											<span>2025년 07월 10일</span> (<span>목요일</span>)
										</td>
									</tr>
									<tr>
										<th scope="row">코스/홀/시간</th>
										<td>IN코스 / 09홀 / 05:18</td>
									</tr>

							
									</tbody>
									</table>


									<hr style="margin:0 0 15px; border:none; border-top:1px dashed #999;">
									
									<table class="cm_time_info_tbl" summary="그린피정보를 알려드립니다">
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