light_source {
    %%pos%%
    color rgb %%color%%
    spotlight
    radius %%fov%%
    falloff %%fov%% + 10
    tightness 1
    fade_distance 1
    fade_power %%att%%
    point_at %%focus%%
    %%arealight%%
}

