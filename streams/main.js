const state = {
	video: document.getElementById('video'),
};

// try {
// 	moment.locale(navigator.language);
// } catch (error) {
// 	moment.locale('uk-UA');
// }

// https://github.com/video-dev/hls.js/blob/master/docs/API.md
$(function () {
	playVideo('test__1');
	setTimeout(() => {
		playVideo('test__2');
	}, 5000);
	setTimeout(() => {
		playVideo('test__3');
	}, 10000);

	// playVideo('rtsp://132.226.223.144:8554/stream/mriya');
	// playVideo('rtmp://132.226.223.144:1935/test__1');
	// playVideo('https://www.youtube.com/watch?v=d46Azg3Pm4c');
	// fetch('http://132.226.223.144:9997/v1/paths/list')
	// 	.then((response) => response.json())
	// 	.then((data) => {
	// 		console.log(data);
	// 	});
});

const playVideo = (streamName) => {
	if (Hls.isSupported()) {
		const videoSrc = `http://132.226.223.144:8888/${streamName}/index.m3u8`;
		hls = new Hls();
		hls.attachMedia(state.video);
		hls.loadSource(videoSrc);
		// setTimeout(() => {
		// 	state.video.play();
		// }, 1000);
	}
};
