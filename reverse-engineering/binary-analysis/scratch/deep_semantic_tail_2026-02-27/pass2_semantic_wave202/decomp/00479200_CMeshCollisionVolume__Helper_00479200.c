/* address: 0x00479200 */
/* name: CMeshCollisionVolume__Helper_00479200 */
/* signature: void __cdecl CMeshCollisionVolume__Helper_00479200(void * param_1, void * param_2, void * param_3, void * param_4, void * param_5) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __cdecl
CMeshCollisionVolume__Helper_00479200
          (void *param_1,void *param_2,void *param_3,void *param_4,void *param_5)

{
  void *pvVar1;
  float fVar2;
  float *extraout_EAX;
  float *extraout_EAX_00;
  float *extraout_EAX_01;
  void *unaff_EBP;
  void *unaff_EDI;
  float10 extraout_ST0;
  float10 extraout_ST0_00;
  float10 extraout_ST0_01;
  float10 extraout_ST0_02;
  float10 fVar3;
  double dVar4;
  float local_60;
  float local_5c;
  float local_58;
  undefined4 local_54;
  float local_50;
  float local_4c;
  float local_48;
  undefined4 local_44;
  float local_40;
  float local_3c;
  float local_38;
  undefined4 local_34;
  float local_30;
  float local_2c;
  float local_28;
  float local_24;
  float local_20;
  float local_1c;
  float local_18;
  undefined1 local_10 [16];

  Vec3__SetXYZ();
  CMeshCollisionVolume__Helper_0040d120(param_2,&local_30,param_3,unaff_EDI);
  CUnitAI__Helper_00477ba0();
  SQRT__Wrapper_00406d50(&local_30);
  dVar4 = CMeshCollisionVolume__Helper_0040d180(&local_30,&local_20,unaff_EDI);
  pvVar1 = (void *)(float)dVar4;
  if ((double)_DAT_005d856c <= dVar4) {
    if ((float)pvVar1 * (float)pvVar1 <= (float)extraout_ST0) {
      Vec3__ScaleToOut(&local_30,local_10,pvVar1,(float)unaff_EDI);
      local_30 = *extraout_EAX;
      local_2c = extraout_EAX[1];
      local_28 = extraout_EAX[2];
      local_24 = extraout_EAX[3];
      Vec3__Add(param_3,&local_60,&local_30,unaff_EDI);
    }
    else {
      local_60 = *(float *)param_2;
      local_5c = *(float *)((int)param_2 + 4);
      local_58 = *(float *)((int)param_2 + 8);
      local_54 = *(undefined4 *)((int)param_2 + 0xc);
    }
  }
  else {
    local_60 = *(float *)param_3;
    local_5c = *(float *)((int)param_3 + 4);
    local_58 = *(float *)((int)param_3 + 8);
    local_54 = *(undefined4 *)((int)param_3 + 0xc);
  }
  Vec3__SetXYZ();
  CMeshCollisionVolume__Helper_0040d120(param_4,&local_30,param_2,unaff_EBP);
  CUnitAI__Helper_00477ba0();
  SQRT__Wrapper_00406d50(&local_30);
  dVar4 = CMeshCollisionVolume__Helper_0040d180(&local_30,&local_20,unaff_EBP);
  pvVar1 = (void *)(float)dVar4;
  if ((double)_DAT_005d856c <= dVar4) {
    if ((float)pvVar1 * (float)pvVar1 <= (float)extraout_ST0_00) {
      Vec3__ScaleToOut(&local_30,local_10,pvVar1,(float)unaff_EBP);
      local_30 = *extraout_EAX_00;
      local_2c = extraout_EAX_00[1];
      local_28 = extraout_EAX_00[2];
      local_24 = extraout_EAX_00[3];
      Vec3__Add(param_2,&local_50,&local_30,unaff_EBP);
    }
    else {
      local_50 = *(float *)param_4;
      local_4c = *(float *)((int)param_4 + 4);
      local_48 = *(float *)((int)param_4 + 8);
      local_44 = *(undefined4 *)((int)param_4 + 0xc);
    }
  }
  else {
    local_50 = *(float *)param_2;
    local_4c = *(float *)((int)param_2 + 4);
    local_48 = *(float *)((int)param_2 + 8);
    local_44 = *(undefined4 *)((int)param_2 + 0xc);
  }
  CMeshCollisionVolume__Helper_0040d120(param_5,&local_20,param_4,unaff_EBP);
  CMeshCollisionVolume__Helper_0040d120(param_3,&local_30,param_4,unaff_EBP);
  CUnitAI__Helper_00477ba0();
  SQRT__Wrapper_00406d50(&local_30);
  dVar4 = CMeshCollisionVolume__Helper_0040d180(&local_30,&local_20,unaff_EBP);
  pvVar1 = (void *)(float)dVar4;
  if ((double)_DAT_005d856c <= dVar4) {
    if ((float)pvVar1 * (float)pvVar1 <= (float)extraout_ST0_01) {
      Vec3__ScaleToOut(&local_30,local_10,pvVar1,(float)unaff_EBP);
      local_30 = *extraout_EAX_01;
      local_2c = extraout_EAX_01[1];
      local_28 = extraout_EAX_01[2];
      local_24 = extraout_EAX_01[3];
      Vec3__Add(param_4,&local_40,&local_30,unaff_EBP);
    }
    else {
      local_40 = *(float *)param_3;
      local_3c = *(float *)((int)param_3 + 4);
      local_38 = *(float *)((int)param_3 + 8);
      local_34 = *(undefined4 *)((int)param_3 + 0xc);
    }
  }
  else {
    local_40 = *(float *)param_4;
    local_3c = *(float *)((int)param_4 + 4);
    local_38 = *(float *)((int)param_4 + 8);
    local_34 = *(undefined4 *)((int)param_4 + 0xc);
  }
  local_30 = *(float *)param_5 - local_60;
  local_2c = *(float *)((int)param_5 + 4) - local_5c;
  local_28 = *(float *)((int)param_5 + 8) - local_58;
  Vec3__SetXYZ();
  fVar2 = local_20 * local_20 + local_1c * local_1c + local_18 * local_18;
  Vec3__SetXYZ();
  CUnitAI__Helper_00477ba0();
  fVar3 = (float10)local_30 * (float10)local_30 +
          (float10)local_2c * (float10)local_2c + (float10)local_28 * (float10)local_28;
  if ((float10)fVar2 < fVar3) {
    fVar3 = (float10)fVar2;
    local_60 = local_50;
    local_5c = local_4c;
    local_58 = local_48;
    local_54 = local_44;
  }
  if (extraout_ST0_02 < fVar3) {
    local_60 = local_40;
    local_5c = local_3c;
    local_58 = local_38;
    local_54 = local_34;
  }
  *(float *)param_1 = local_60;
  *(float *)((int)param_1 + 4) = local_5c;
  *(float *)((int)param_1 + 8) = local_58;
  *(undefined4 *)((int)param_1 + 0xc) = local_54;
  return;
}
