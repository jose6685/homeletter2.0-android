package org.homeletter.app;

import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.util.Log;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import com.google.android.gms.ads.AdError;
import com.google.android.gms.ads.AdRequest;
import com.google.android.gms.ads.LoadAdError;
import com.google.android.gms.ads.MobileAds;
import com.google.android.gms.ads.OnPaidEventListener;
import com.google.android.gms.ads.rewarded.OnUserEarnedRewardListener;
import com.google.android.gms.ads.rewarded.RewardItem;
import com.google.android.gms.ads.rewarded.RewardedAd;
import com.google.android.gms.ads.rewarded.RewardedAdLoadCallback;
import com.google.android.gms.ads.FullScreenContentCallback;

public class RewardedAdActivity extends AppCompatActivity {

    private static final String TAG = "HomeLetterRewarded";
    private static final String AD_UNIT_ID = "ca-app-pub-9507923681356448/8178860305";
    private RewardedAd rewardedAd = null;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        try {
            MobileAds.initialize(this);
        } catch (Throwable t) {
            Log.w(TAG, "MobileAds.initialize threw", t);
        }
        loadAndShow();
    }

    private void loadAndShow() {
        AdRequest request = new AdRequest.Builder().build();
        RewardedAd.load(
                this,
                AD_UNIT_ID,
                request,
                new RewardedAdLoadCallback() {
                    @Override
                    public void onAdLoaded(@NonNull RewardedAd ad) {
                        rewardedAd = ad;
                        Log.d(TAG, "Rewarded loaded");
                        setCallbacksAndShow(ad);
                    }

                    @Override
                    public void onAdFailedToLoad(@NonNull LoadAdError loadAdError) {
                        Log.w(TAG, "Rewarded failed to load: " + loadAdError);
                        finish();
                    }
                }
        );
    }

    private void setCallbacksAndShow(RewardedAd ad) {
        ad.setFullScreenContentCallback(new FullScreenContentCallback() {
            @Override
            public void onAdShowedFullScreenContent() {
                Log.d(TAG, "Rewarded showed");
            }

            @Override
            public void onAdDismissedFullScreenContent() {
                Log.d(TAG, "Rewarded dismissed");
                navigateBackWithRewardFlag(false);
                rewardedAd = null;
                finish();
            }

            @Override
            public void onAdFailedToShowFullScreenContent(@NonNull AdError adError) {
                Log.w(TAG, "Rewarded failed to show: " + adError);
                finish();
            }
        });

        ad.setOnPaidEventListener(new OnPaidEventListener() {
            @Override
            public void onPaidEvent(@NonNull com.google.android.gms.ads.AdValue adValue) {
                Log.d(TAG, "Paid event: " + adValue.getValueMicros());
            }
        });

        ad.show(this, new OnUserEarnedRewardListener() {
            @Override
            public void onUserEarnedReward(@NonNull RewardItem rewardItem) {
                Log.d(TAG, "User earned reward: " + rewardItem.getAmount());
                navigateBackWithRewardFlag(true);
            }
        });
    }

    private void navigateBackWithRewardFlag(boolean earned) {
        try {
            String launchUrl = getString(R.string.launchUrl);
            if (launchUrl == null) return;
            String sep = launchUrl.contains("?") ? "&" : "?";
            Uri uri = Uri.parse(launchUrl + sep + "rewarded=" + (earned ? "1" : "0"));
            Intent intent = new Intent(Intent.ACTION_VIEW, uri);
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            startActivity(intent);
        } catch (Throwable t) {
            Log.w(TAG, "navigateBackWithRewardFlag failed", t);
        }
    }
}