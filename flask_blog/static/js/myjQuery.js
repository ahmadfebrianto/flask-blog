$(document).ready(()=>{
	$(".alert").fadeTo(2000, 500).slideUp(500,() => {
		$(".alert").slideUp(500);
	});
	detectPostLang();
})


const images_path = "/static/images"

const editPost = (postId, newPost, oldPost) => {
	$(oldPost).html(`<img src='${images_path}/gifs/loading.gif'>`);
	$.post(`/post/${postId}/edit`, {
		new_post: $(newPost).val()
	}).done((response) => {
		$(oldPost).text(response['new_post']),
			detectPostLang(postId=postId)
	}).fail(() => {
		$(postBody).text("{{ _('Error: Could not contact server.') }}");
	});
}


const detectPostLang = (postId=null) => {
	if (postId != null) {
		$(`#trans-btn-${postId}`).hide();
		$(`#translation-result-${postId}`).hide();

		let postText = $(`#post-${postId}`).text();
		let postItems = [postId, postText]
		$.post('/detect-language', {
			post_items: `${postItems}`
		}).done((response) => {
			let gLocale = $('#g-locale').text();
			result = response['results']
			if (result[1] != gLocale) {
				let id = result[0].slice(-1);
				$(`#trans-btn-${id}`).show();
				$(`#hidden-td-${postId}`).hide()
			}
		})

	} else {
		$('.trans-btn').hide();
		$('.translation-result').hide();
	
		let postItems = [];
		$('.post-item').each(function(index){
			let postId = $(this).attr('id');
			let postText = $(this).text();
			postItems.push([postId, postText]);
		});
	
		$.post(`/detect-language`, {
			post_items: `${postItems}`
		}).done((response) => {
			let gLocale = $('#g-locale').text();
			response['results'].forEach(result => {
				if (result[1] != gLocale) {
					let id = result[0].slice(-1);
					$(`#trans-btn-${id}`).show();
				}
			})
		})
	}
}


const translate = (postId, postElem, transDestElem, destLang) => {
	$(`#hidden-td-${postId}`).show()
	$(`#trans-btn-${postId}`).hide()
	$(`#loading-${postId}`).show()
	$.post(`/post/${postId}/translate`, {
		origin_text: $(postElem).text(),
		dest_lang: destLang,
	}).done((response) => {
		$(`#loading-${postId}`).hide()
		$(`${transDestElem}>small`).html(response['result']),
			$(transDestElem).show()
	})
}




