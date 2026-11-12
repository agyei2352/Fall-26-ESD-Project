% Exploratory pulse response model matching the Multisim Rskin || Cskin network.
% R/C values are sensitivity-study inputs, not validated human-skin parameters.
clc; clear; close all;

Vdrive = 3.0; % CR2032 nominal voltage at the bare nRF52840 supply.
Rlimit = 1e6;
Rground = 1e6;
testResistance = [500e3, 1e6, 2e6, 5e6, 10e6, 20e6, 35e6, 40e6, inf];

% Resistance thresholds use the settled pulse plateau (DC result).
adcVoltage = zeros(size(testResistance));
for index = 1:numel(testResistance)
    skin = testResistance(index);
    if isfinite(skin)
        adcVoltage(index) = Vdrive * Rground / (Rlimit + skin + Rground);
    end
end

status = strings(size(testResistance));
status(testResistance < 5e6 & isfinite(testResistance)) = "GOOD";
status(testResistance >= 5e6 & testResistance <= 35e6) = "WARNING";
status(testResistance > 35e6 | isinf(testResistance)) = "FAIL";
unclassified = status == "";
status(unclassified) = "FAIL";

statusTable = table(testResistance(:), adcVoltage(:), status(:), ...
    'VariableNames', {'SkinResistanceOhms', 'PlateauVoltageV', 'Status'});
disp(statusTable);
outputDirectory = fileparts(mfilename('fullpath'));
writetable(statusTable, fullfile(outputDirectory, 'ESD_Wristband_Status_Calculations.csv'));

% Change resistance or capacitance separately to compare waveform features.
scenarioNames = ["Baseline: 500k, 1nF"; ...
                 "Higher R: 5M, 1nF"; ...
                 "Higher C: 500k, 10nF"; ...
                 "Worst-case RC: 40M, 10nF"];
scenarioResistance = [500e3; 5e6; 500e3; 40e6];
scenarioCapacitance = [1e-9; 1e-9; 10e-9; 10e-9];

pulseWidth = 75e-3; % Characterization profile; not the resistance-classification window.
pulsePeriod = 1.075;
timeStep = 5e-6;
time = (0:timeStep:80e-3)';
waveforms = zeros(numel(time), numel(scenarioNames));
earlyVoltage = zeros(numel(scenarioNames), 1);
plateauVoltage = zeros(numel(scenarioNames), 1);
settlingTimeTransient = zeros(numel(scenarioNames), 1);
settlingTimeFinal = zeros(numel(scenarioNames), 1);

for scenario = 1:numel(scenarioNames)
    skinR = scenarioResistance(scenario);
    skinC = scenarioCapacitance(scenario);
    waveforms(:, scenario) = simulatePulse(...
        time, Vdrive, Rlimit, Rground, skinR, skinC, pulseWidth, pulsePeriod);

    plateauVoltage(scenario) = Vdrive * Rground / ...
        (Rlimit + Rground + skinR);
    earlyIndex = find(time >= 25e-6, 1);
    earlyVoltage(scenario) = waveforms(earlyIndex, scenario);
    timeConstant = (Rlimit + Rground) * skinR * skinC / ...
        (Rlimit + Rground + skinR);
    initialVoltage = Vdrive * Rground / (Rlimit + Rground);
    transientAmplitude = abs(initialVoltage - plateauVoltage(scenario));
    settlingTimeTransient(scenario) = -log(0.05) * timeConstant;
    settlingTimeFinal(scenario) = -timeConstant * log(...
        0.05 * abs(plateauVoltage(scenario)) / transientAmplitude);
end

waveformFeatures = table(scenarioNames, scenarioResistance, scenarioCapacitance, ...
    earlyVoltage, plateauVoltage, earlyVoltage - plateauVoltage, ...
    settlingTimeTransient * 1e3, settlingTimeFinal * 1e3, ...
    'VariableNames', {'Scenario', 'SkinResistanceOhms', 'SkinCapacitanceF', ...
    'EarlyVoltageV', 'PlateauVoltageV', 'EdgeDropV', ...
    'SettlingTime5PctTransientMs', 'SettlingTime5PctFinalMs'});
disp('Illustrative waveform feature comparison:');
disp(waveformFeatures);
writetable(waveformFeatures, ...
    fullfile(outputDirectory, 'ESD_Wristband_Waveform_Calculations.csv'));

% Compare actual firmware-style late-window averages for the slowest RC case.
worstSkinResistance = 40e6;
worstSkinCapacitance = 10e-9;
classificationPulseWidth = 250e-3;
classificationCyclePeriod = 1.25; % 250 ms measurement + 200 ms blink + 800 ms sleep.
lateSampleCount = 50;
sampleInterval = 250e-6;
saadcAcquisitionTime = 40e-6; % Provisional from review; verify exact SoC/SDK configuration.
characterizationTicks = (250:299)';
classificationTicks = (950:999)';
characterizationTriggerTimes = characterizationTicks * sampleInterval;
classificationTriggerTimes = classificationTicks * sampleInterval;
% Approximate sample-capacitor capture at the end of the acquisition interval.
characterizationTimes = characterizationTriggerTimes + saadcAcquisitionTime;
classificationTimes = classificationTriggerTimes + saadcAcquisitionTime;

worstPlateau = Vdrive * Rground / ...
    (Rlimit + worstSkinResistance + Rground);
worstInitial = Vdrive * Rground / (Rlimit + Rground);
worstTau = (Rlimit + Rground) * worstSkinResistance * worstSkinCapacitance / ...
    (Rlimit + Rground + worstSkinResistance);
worstT95OfFinal = -worstTau * log(0.05 * worstPlateau / (worstInitial - worstPlateau));

characterizationVoltages = worstPlateau + ...
    (worstInitial - worstPlateau) .* exp(-characterizationTimes / worstTau);
classificationVoltages = worstPlateau + ...
    (worstInitial - worstPlateau) .* exp(-classificationTimes / worstTau);
characterizationAverage = mean(characterizationVoltages);
classificationAverage = mean(classificationVoltages);
characterizationResistance = (Vdrive * Rground / characterizationAverage) - Rlimit - Rground;
classificationResistance = (Vdrive * Rground / classificationAverage) - Rlimit - Rground;

classificationEndTime = classificationTriggerTimes(end) + saadcAcquisitionTime;
classificationFallTime = classificationPulseWidth;
classificationFallMargin = classificationFallTime - classificationEndTime;
windowBiasCheck = table(...
    ["75 ms characterization"; "250 ms classification"], ...
    [characterizationTriggerTimes(1); classificationTriggerTimes(1)] * 1e3, ...
    [characterizationTriggerTimes(end); classificationTriggerTimes(end)] * 1e3, ...
    [characterizationTimes(end); classificationTimes(end)] * 1e3, ...
    [characterizationAverage; classificationAverage], ...
    [characterizationResistance; classificationResistance] / 1e6, ...
    ["WARNING"; "FAIL"], ...
    'VariableNames', {'Profile', 'FirstTriggerMs', 'LastTriggerMs', ...
    'LastCaptureCompleteMs', 'AverageSenseVoltageV', ...
    'InferredResistanceMOhm', 'ExpectedStatus'});
disp('Worst-case 40 MOhm / 10 nF late-window bias check:');
fprintf('True plateau %.5f V; tau %.3f ms; 5%%-of-final settling %.3f ms.\n', ...
    worstPlateau, worstTau * 1e3, worstT95OfFinal * 1e3);
fprintf('Classification pulse falls at %.3f ms; last capture completes at %.3f ms; margin %.3f ms. SAADC acquisition %.0f us is provisional.\n', ...
    classificationFallTime * 1e3, classificationEndTime * 1e3, ...
    classificationFallMargin * 1e3, saadcAcquisitionTime * 1e6);
disp(windowBiasCheck);
writetable(windowBiasCheck, ...
    fullfile(outputDirectory, 'ESD_Wristband_Window_Bias_Check.csv'));

driveWaveform = Vdrive * (mod(time, pulsePeriod) < pulseWidth);
figure('Color', 'white', 'Position', [100 100 900 600]);
plot(time * 1e3, waveforms, 'LineWidth', 1.5);
hold on;
plot(time * 1e3, driveWaveform, 'k--', 'LineWidth', 1);
xlim([0 80]);
xlabel('Time (ms)');
ylabel('Voltage (V)');
title('Pulse Edge and Settling at the ADC Sense Node');
legend([scenarioNames; "Drive pulse"], 'Location', 'northeast');
grid on;

function output = simulatePulse(time, drive, rLimit, rGround, rSkin, cSkin, width, period)
totalSeries = rLimit + rGround;
dcGain = rGround / (totalSeries + rSkin);
edgeGain = rGround / totalSeries;
tau = totalSeries * rSkin * cSkin / (totalSeries + rSkin);
output = zeros(size(time));

for pulseStart = 0:period:time(end)
    edgeTimes = [pulseStart, pulseStart + width];
    edgeSigns = [1, -1];
    for edge = 1:2
        age = time - edgeTimes(edge);
        active = age >= 0;
        stepResponse = dcGain + (edgeGain - dcGain) .* exp(-age(active) / tau);
        output(active) = output(active) + edgeSigns(edge) * drive * stepResponse;
    end
end
end
