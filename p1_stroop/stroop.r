# File:    stroop.r
# Purpose: Exploratory data analysis of a dataset from a color Stroop experiment with N=24
# Author:  Ivailo Kassamakov
# Date:    23.Aug.2015

# Read in the dataset
stroop <- read.csv("stroopdata.csv", header=TRUE, sep=",")

# Statistical summary
sum <- summary(stroop)
print(sum)

# Boxplot
png(file = "boxplot.png", bg = "white")
boxplot(stroop, boxwex=0.25, col=c("green","red"), frame=FALSE, ylab="Set Completion Time [s]")
dev.off()

# Barplot
png(file = "barplot.png", bg = "white")
sm <- t(as.matrix(stroop))
barplot(sm, beside=TRUE, col=c("green","red"), leg=TRUE, xlab="Participant", 
        ylab="Set Completion Time [s]", space=c(0,1.5), names.arg=seq(1,24))
dev.off()

# Removing the outliers in rows 15 and 20 of the original dataset
strclean <- stroop[-c(15,20),]

# Histogram of outlier-free dataset
png(file = "hist.png", bg = "white")
par(mfrow=c(2,1))
hist(strclean$Congruent, col="green", freq = FALSE, breaks="Sturges")
lines(density(strclean$Congruent, bw="SJ"))
hist(strclean$Incongruent, col="red", freq = FALSE, breaks="Sturges")
lines(density(strclean$Incongruent, bw="SJ"))
dev.off()

# Test for normality
png(file = "qqnorm.png", bg = "white")
par(mfrow=c(2,1))
qqnorm(strclean$Congruent, col="green", main="Normal Q-Q Plot for Congruent Stroop Condition"); qqline(strclean$Congruent)
qqnorm(strclean$Incongruent, col="red", main="Normal Q-Q Plot for Incongruent Stroop Condition"); qqline(strclean$Incongruent)
dev.off()

shapiro.result.congr <- shapiro.test(strclean$Congruent)
print(shapiro.result.congr)
shapiro.result.incongr <- shapiro.test(strclean$Incongruent)
print(shapiro.result.incongr)


########### GROUP DIFFERENCES

diff = stroop$Incongruent - stroop$Congruent
print(diff)

diffcl = strclean$Incongruent - strclean$Congruent
print(diffcl)

# Boxplot of the differences
png(file = "boxplot-diffcl.png", bg = "white")
boxplot(diffcl, boxwex=0.25, col="blue", range=1.5, frame=FALSE, ylab="Set Completion Time [s]")
dev.off()

# Normality of the group differences
png(file = "qqnorm-diffcl.png", bg = "white")
qqnorm(diffcl, col="blue", main="Normal Q-Q Plot for Stroop test"); qqline(diffcl)
dev.off()

# Histogram of the group differences
png(file = "hist-diffcl.png", bg = "white")
hist(diffcl, col="blue", xlab = "Group differences", freq = FALSE, breaks="Sturges")
lines(density(diffcl, bw="SJ"))
dev.off()

# Shapiro-Wilk normality test of the group differences
shapiro.result.diffcl <- shapiro.test(diffcl)
print(shapiro.result.diffcl)


############## T-Test

tcrit = qt(0.05, 21, lower.tail = FALSE)
ttest = t.test(strclean$Incongruent, y=strclean$Congruent, paired=TRUE, alternative="g")

png(file = "ttest.png", bg = "white")
xt<-seq(-4,10,0.001)
plot(xt,dt(xt,21), type = 'l', main = "Visualization of the results of the one-tailed t-test")
polygon(x=c(tcrit,seq(tcrit,ttest$statistic,0.001),ttest$statistic),y=c(0,dt(seq(tcrit,ttest$statistic,0.001),21),0),col="red")
tcrit.text <- paste("tcrit =", formatC(tcrit,4))
tstat.text <- paste("t =", formatC(ttest$statistic,4))
text(x=tcrit, y=-0.01, labels = tcrit.text, col="red")
text(x=ttest$statistic, y=-0.01, labels = tstat.text, col="red")
dev.off()

# EOF

