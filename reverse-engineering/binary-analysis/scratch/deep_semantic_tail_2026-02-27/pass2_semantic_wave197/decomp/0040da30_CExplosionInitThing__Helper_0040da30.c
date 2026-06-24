/* address: 0x0040da30 */
/* name: CExplosionInitThing__Helper_0040da30 */
/* signature: void * __thiscall CExplosionInitThing__Helper_0040da30(void * this, int param_1, void * param_2) */


void * __thiscall CExplosionInitThing__Helper_0040da30(void *this,int param_1,void *param_2)

{
  void *pvVar1;
  void *extraout_EAX;
  void *extraout_EAX_00;
  float extraout_EAX_01;
  float extraout_EAX_02;
  void *extraout_EAX_03;
  void *extraout_EAX_04;
  void *unaff_EDI;
  float local_134;
  float local_130;
  float local_12c;
  void *local_124;
  float local_120;
  float local_11c;
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

  pvVar1 = DAT_008a9e44;
  local_120 = (*(float *)((int)this + 0x1c) - *(float *)((int)this + 0x8c)) * (float)DAT_008a9e44;
  local_11c = (*(float *)((int)this + 0x20) - *(float *)((int)this + 0x90)) * (float)DAT_008a9e44;
  local_134 = local_120 + *(float *)((int)this + 0x8c);
  local_130 = local_11c + *(float *)((int)this + 0x90);
  local_12c = (float)DAT_008a9e44 * (*(float *)((int)this + 0x24) - *(float *)((int)this + 0x94)) +
              *(float *)((int)this + 0x94);
  CMeshCollisionVolume__Helper_0040d120
            ((void *)((int)this + 0x5c),&local_120,(void *)((int)this + 0xbc),unaff_EDI);
  CMeshCollisionVolume__Helper_0040d120
            ((void *)((int)this + 0x4c),local_60,(void *)((int)this + 0xac),extraout_EAX);
  CMeshCollisionVolume__Helper_0040d120
            ((void *)((int)this + 0x3c),local_70,(void *)((int)this + 0x9c),extraout_EAX_00);
  Mat34__SetRows();
  CExplosionInitThing__Helper_0040d150(local_c0,local_50,pvVar1,(float)unaff_EDI);
  CExplosionInitThing__Helper_0040d150(local_d0,local_b0,pvVar1,extraout_EAX_01);
  CExplosionInitThing__Helper_0040d150(local_e0,local_80,pvVar1,extraout_EAX_02);
  Mat34__SetRows();
  Vec3__Add(local_f0,local_40,(void *)((int)this + 0xbc),unaff_EDI);
  Vec3__Add(local_100,local_a0,(void *)((int)this + 0xac),extraout_EAX_03);
  Vec3__Add(local_110,local_90,(void *)((int)this + 0x9c),extraout_EAX_04);
  Mat34__SetRows();
  local_124 = (void *)((*(float *)((int)this + 0x500) - *(float *)((int)this + 0x508)) *
                       (float)DAT_008a9e44 + *(float *)((int)this + 0x508));
  CSquadNormal__Helper_004062d0
            (local_110,local_124,
             (*(float *)((int)this + 0x504) - *(float *)((int)this + 0x50c)) * (float)DAT_008a9e44 +
             *(float *)((int)this + 0x50c),0.0,(float)unaff_EDI);
  CMCBuggy__Helper_0040d320(local_30,local_e0,local_110,unaff_EDI);
  Vec3__SetXYZ();
  Vec3__Add(&local_134,(void *)param_1,&local_120,unaff_EDI);
  return (void *)param_1;
}
