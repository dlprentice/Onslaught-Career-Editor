/* address: 0x0040d7c0 */
/* name: CExplosionInitThing__BuildInterpolatedViewpointTransform */
/* signature: void * __thiscall CExplosionInitThing__BuildInterpolatedViewpointTransform(void * this, int param_1, void * param_2) */


void * __thiscall
CExplosionInitThing__BuildInterpolatedViewpointTransform(void *this,int param_1,void *param_2)

{
  void *pvVar1;
  void *extraout_EAX;
  void *extraout_EAX_00;
  float extraout_EAX_01;
  float extraout_EAX_02;
  void *extraout_EAX_03;
  void *extraout_EAX_04;
  void *unaff_EDI;
  float local_1b0;
  float local_1ac;
  float local_1a0;
  float local_19c;
  float local_198;
  undefined1 local_190 [4];
  float local_18c;
  float local_188;
  float local_180;
  float local_17c;
  float local_178;
  float local_170;
  float local_16c;
  float local_168;
  undefined1 local_160 [16];
  undefined1 local_150 [16];
  undefined1 local_140 [16];
  undefined1 local_130 [16];
  undefined1 local_120 [16];
  undefined1 local_110 [16];
  undefined1 local_100 [16];
  undefined1 local_f0 [16];
  undefined1 local_e0 [16];
  undefined1 local_d0 [16];
  undefined1 local_c0 [16];
  undefined1 local_b0 [16];
  undefined1 local_a0 [16];
  undefined1 local_90 [16];
  undefined1 local_80 [16];
  undefined1 local_70 [16];
  undefined1 local_60 [16];
  undefined1 local_50 [16];
  undefined1 local_40 [16];
  undefined1 local_30 [48];

  CPlayer__GetCurrentViewPoint(*(void **)((int)this + 0x574),(int)&local_170,unaff_EDI);
  CPlayer__GetCurrentViewOrientation(*(void **)((int)this + 0x574),(int)local_d0,unaff_EDI);
  CPlayer__GetOldCurrentViewPoint(*(void **)((int)this + 0x574),(int)&local_1a0,unaff_EDI);
  CPlayer__GetOldCurrentViewOrientation(*(void **)((int)this + 0x574),(int)local_160,unaff_EDI);
  pvVar1 = DAT_008a9e44;
  local_18c = local_16c - local_19c;
  local_188 = local_168 - local_198;
  local_1b0 = (local_170 - local_1a0) * (float)DAT_008a9e44;
  local_1ac = local_18c * (float)DAT_008a9e44;
  local_180 = local_1b0 + local_1a0;
  local_17c = local_1ac + local_19c;
  local_178 = (float)DAT_008a9e44 * local_188 + local_198;
  CMeshCollisionVolume__Helper_0040d120(local_b0,&local_1b0,local_140,unaff_EDI);
  CMeshCollisionVolume__Helper_0040d120(local_c0,local_190,local_150,extraout_EAX);
  CMeshCollisionVolume__Helper_0040d120(local_d0,local_90,local_160,extraout_EAX_00);
  Mat34__SetRows();
  Vec3__ScaleToOut(local_e0,local_60,pvVar1,(float)unaff_EDI);
  Vec3__ScaleToOut(local_f0,local_a0,pvVar1,extraout_EAX_01);
  Vec3__ScaleToOut(local_100,local_70,pvVar1,extraout_EAX_02);
  Mat34__SetRows();
  Vec3__Add(local_110,local_50,local_140,unaff_EDI);
  Vec3__Add(local_120,local_80,local_150,extraout_EAX_03);
  Vec3__Add(local_130,local_40,local_160,extraout_EAX_04);
  Mat34__SetRows();
  CSquadNormal__Helper_004062d0
            (local_130,
             (void *)((*(float *)((int)this + 0x4e8) - *(float *)((int)this + 0x4ec)) *
                      (float)DAT_008a9e44 + *(float *)((int)this + 0x4ec)),
             (*(float *)((int)this + 0x4f4) - *(float *)((int)this + 0x4f8)) * (float)DAT_008a9e44 +
             *(float *)((int)this + 0x4f8),0.0,(float)unaff_EDI);
  CMCBuggy__Helper_0040d320(local_30,local_100,local_130,unaff_EDI);
  Vec3__SetXYZ();
  Vec3__Add(&local_180,(void *)param_1,&local_1b0,unaff_EDI);
  return (void *)param_1;
}
