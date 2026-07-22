# Next Plan

1. 実際のagent traceからprompt、tool schema、output length、arrival timingを匿名化してreplayする。
2. FP8のs4/s8/s16をconcurrency 1中心に3回以上反復し、varianceを測る。
3. tool-call JSON、短いfinal answer、長いsynthesisを別bucketで集計する。
4. requestごとのoutput budgetまたはphaseに応じてspec depthを4/8へ切り替えるpolicyを評価する。
5. prefix cache hit率、batch size、EOS終了率を同時記録し、職場slowdownの残差を説明する。
