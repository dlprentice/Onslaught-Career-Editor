/* address: 0x004804c0 */
/* name: CExplosionInitThing__Unk_004804c0 */
/* signature: void __thiscall CExplosionInitThing__Unk_004804c0(void * this, int param_1, void * param_2) */


void __thiscall CExplosionInitThing__Unk_004804c0(void *this,int param_1,void *param_2)

{
  char cVar1;
  int *unaff_ESI;
  int *unaff_EDI;
  float10 fVar2;
  int *unaff_retaddr;

  cVar1 = (**(code **)(*(int *)param_1 + 0x50))();
  if (cVar1 != '\0') {
    fVar2 = (float10)(**(code **)(*(int *)param_1 + 0x34))();
    *(float *)(*(int *)((int)this + 0x208) + 0x20) = (float)fVar2;
    return;
  }
  cVar1 = (**(code **)(*(int *)param_1 + 0x50))();
  if (cVar1 != '\0') {
    fVar2 = (float10)(**(code **)(*unaff_retaddr + 0x34))();
    *(float *)(*(int *)((int)this + 0x208) + 0x24) = (float)fVar2;
    return;
  }
  cVar1 = (**(code **)(*(int *)param_1 + 0x50))();
  if (cVar1 != '\0') {
    fVar2 = (float10)(**(code **)(*unaff_ESI + 0x34))();
    *(float *)(*(int *)((int)this + 0x208) + 0x28) = (float)fVar2;
    return;
  }
  cVar1 = (**(code **)(*(int *)param_1 + 0x50))();
  if (cVar1 != '\0') {
    fVar2 = (float10)(**(code **)(*unaff_EDI + 0x34))();
    *(float *)((int)this + 0x29c) = (float)fVar2;
    return;
  }
  cVar1 = (**(code **)(*(int *)param_1 + 0x50))();
  if (cVar1 != '\0') {
    fVar2 = (float10)(**(code **)(s_hb_maxvelx_0062cddc._0_4_ + 0x34))();
    *(float *)((int)this + 0x288) = (float)fVar2;
    return;
  }
  cVar1 = (**(code **)(*(int *)param_1 + 0x50))();
  if (cVar1 != '\0') {
    fVar2 = (float10)(**(code **)(s_hb_maxvely_0062cdd0._0_4_ + 0x34))();
    *(float *)((int)this + 0x284) = (float)fVar2;
    return;
  }
  cVar1 = (**(code **)(*(int *)param_1 + 0x50))();
  if (cVar1 != '\0') {
    fVar2 = (float10)(**(code **)(s_hb_maxvelz_0062cdc4._0_4_ + 0x34))();
    *(float *)((int)this + 0x290) = (float)fVar2;
    return;
  }
  cVar1 = (**(code **)(*(int *)param_1 + 0x50))();
  if (cVar1 != '\0') {
    fVar2 = (float10)(**(code **)(s_hb_rotate_speed_0062cdb4._0_4_ + 0x34))();
    *(float *)((int)this + 0x28c) = (float)fVar2;
    return;
  }
  cVar1 = (**(code **)(*(int *)param_1 + 0x50))(s_hb_core_bot_inner_rotate_speed_0062cd14);
  if (cVar1 != '\0') {
    fVar2 = (float10)(**(code **)(s_hb_core_top_inner_rotate_speed_0062cd94._0_4_ + 0x34))();
    *(float *)((int)this + 0x298) = (float)fVar2;
    return;
  }
  cVar1 = (**(code **)(*(int *)param_1 + 0x50))(s_hb_core_bot_outer_rotate_speed_0062ccf4);
  if (cVar1 != '\0') {
    fVar2 = (float10)(**(code **)(s_hb_core_top_outer_rotate_speed_0062cd74._0_4_ + 0x34))();
    *(float *)((int)this + 0x294) = (float)fVar2;
    return;
  }
  cVar1 = (**(code **)(*(int *)param_1 + 0x50))(s_hb_safe_dist_0062cce4);
  if (cVar1 != '\0') {
    fVar2 = (float10)(**(code **)(s_hb_core_mid_inner_rotate_speed_0062cd54._0_4_ + 0x34))();
    *(float *)((int)this + 0x2a0) = (float)fVar2;
    return;
  }
  cVar1 = (**(code **)(*(int *)param_1 + 0x50))(s_hb_min_height_above_ground_0062ccc8);
  if (cVar1 != '\0') {
    fVar2 = (float10)(**(code **)(s_hb_core_mid_outer_rotate_speed_0062cd34._0_4_ + 0x34))();
    *(float *)((int)this + 0x268) = (float)fVar2;
    return;
  }
  CExplosionInitThing__Helper_004f45e0((void *)param_1);
  return;
}
