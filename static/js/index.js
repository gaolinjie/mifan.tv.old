
  $(document).ready(function(){


  $(document).on('click', '.post-comment',  function() {
    var comment_editor = $(this).parent().parent().parent();
    var comment_card = $(this).parent().parent().parent().parent().parent().find(".comment-card");
    var post_id = $(this).parent().parent().parent().parent().find('.bottom').find('input').val();
    var comment_content = $(".editor-box").val();
    $.post("/comment", 
      {post_id: post_id,
        comment_content: comment_content})
    .done(function() {
      comment_editor.hide();
      comment_card.html('<div class="divider"></div>
      <div class="c-num">
        <a class="c-link">{{ post.comment_count }} 条评论</a>
        <span class="c-icon"></span>
      </div>
      <div class="comment-list">
        <div class="ftRt " >
          <ul class="jspScrollable" tabindex="" >
            <li>
              <div class="pic">
                <a href="http://weibo.com/3097378697" target="_blank">
                  <img src="https://lh3.googleusercontent.com/-z2uoLUyWCqw/AAAAAAAAAAI/AAAAAAAAAAA/HTCi3KBuPc4/s28-c-k-no/photo.jpg" alt="头像"></a>
              </div>
              <div class="doSth">
                <p>
                  <a class="mb_name" href="http://weibo.com/3097378697" target="_blank">Zealer中国</a>
                </p>
                <p>
                  <span class="time">下午11:05</span>
                </p>
                <p>
                  <span class="text" href="http://api.t.sina.com.cn/3097378697/statuses/3614910061880559">
                    超精准“抛投”！！[赞] 你以为所有事情都如此简单？短短几分钟的视频，该国外团队却花了一年时间左右拍摄。http://t.cn/z8hMCAJ
                  </span>
                </p>
              </div>
            </li>
            
          </ul>
        </div>
      </div>
      <div class="divider" style=""></div>
      <div class="comment-input-wraper">
        <div class="comment-box" tabindex="0" role="button">发表评论...</div>
      </div>');
    })
    .fail(function() { alert("error"); })
  });
});


  

