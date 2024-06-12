docker:
	docker buildx build --platform linux/arm64 --load \
		-t 592247757306.dkr.ecr.ap-northeast-2.amazonaws.com/docs-ai-scrap:latest  .

docker:
	docker push 592247757306.dkr.ecr.ap-northeast-2.amazonaws.com/docs-ai-scrap:latest
