/* address: 0x00411630 */
/* name: CMonitor__Unk_00411630 */
/* signature: void __fastcall CMonitor__Unk_00411630(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CMonitor__Unk_00411630(int param_1)

{
  int iVar1;
  float fVar2;
  float fVar3;
  undefined4 *puVar4;
  float unaff_ESI;
  double dVar5;
  undefined1 *puVar6;
  float fStack_bc;
  float local_b4;
  undefined4 uStack_b0;
  undefined4 uStack_ac;
  undefined4 uStack_a8;
  float fStack_a4;
  undefined4 uStack_a0;
  undefined4 uStack_9c;
  undefined4 uStack_98;
  undefined4 uStack_94;
  undefined4 local_90;
  float local_8c;
  undefined4 local_88;
  undefined4 uStack_74;
  undefined4 uStack_70;
  float fStack_6c;
  undefined4 uStack_68;
  undefined4 uStack_64;
  undefined4 uStack_60;
  undefined4 uStack_5c;
  undefined4 uStack_58;
  undefined4 uStack_54;
  undefined4 uStack_50;
  undefined4 uStack_4c;
  undefined4 uStack_48;
  undefined4 uStack_44;
  undefined4 uStack_40;
  undefined4 uStack_3c;
  undefined4 uStack_38;
  undefined1 auStack_34 [4];
  undefined1 local_30 [8];
  float local_28;
  undefined1 auStack_24 [8];
  float fStack_1c;
  undefined1 local_10 [16];

  Vec3__SetXYZ();
  Vec3__SetXYZ();
  fVar3 = DAT_006fbdfc;
  dVar5 = CHeightField__Unk_0047eb80(0x6fadc8,local_30);
  local_b4 = (float)dVar5;
  fVar2 = local_b4;
  if (fVar3 < local_b4) {
    fVar2 = fVar3;
  }
  if ((*(float *)(*(int *)(param_1 + 0x18) + 0xfc) != _DAT_005d856c) &&
     (fVar2 - local_28 < _DAT_005d85d8)) {
    Vec3__SetXYZ();
    puVar6 = local_10;
    (**(code **)(**(int **)(param_1 + 0x18) + 0x74))();
    if ((*(int *)(param_1 + 0x2c) == 0) && (*(float *)(param_1 + 0x48) == _DAT_005d856c)) {
      iVar1 = *(int *)(param_1 + 0x18);
      if (_DAT_005d856c < *(float *)(iVar1 + 0x84)) {
        *(float *)(iVar1 + 0x84) = *(float *)(iVar1 + 0x84) * _DAT_005d8bb0;
      }
      fVar2 = *(float *)(*(int *)(param_1 + 0x18) + 0x114);
      vector_constructor_iterator_nothrow(&uStack_64,0x10,3,&LAB_00402d20);
      fsin((float10)fVar2);
      fcos((float10)fVar2);
      puVar4 = (undefined4 *)Vec3__SetXYZ();
      uStack_64 = *puVar4;
      uStack_60 = puVar4[1];
      uStack_5c = puVar4[2];
      uStack_58 = puVar4[3];
      puVar4 = (undefined4 *)Vec3__SetXYZ();
      uStack_54 = *puVar4;
      uStack_50 = puVar4[1];
      uStack_4c = puVar4[2];
      uStack_48 = puVar4[3];
      puVar4 = (undefined4 *)Vec3__SetXYZ();
      uStack_44 = *puVar4;
      uStack_40 = puVar4[1];
      uStack_3c = puVar4[2];
      uStack_38 = puVar4[3];
      Vec3__SetXYZ();
      if (fStack_bc <= fVar3) {
        fStack_a4 = 0.0;
        uStack_a0 = 0;
        uStack_9c = 0xbf800000;
        uStack_98 = uStack_a8;
      }
      else {
        CHeightField__Unk_0047ec60(0x6fadc8,&local_b4,auStack_34);
        fStack_a4 = local_b4;
        uStack_a0 = uStack_b0;
        uStack_9c = uStack_ac;
        uStack_98 = uStack_a8;
      }
      local_b4 = fStack_a4;
      uStack_b0 = uStack_a0;
      uStack_ac = uStack_9c;
      Vec3__SetXYZ();
      Vec3__Cross(&uStack_74,auStack_24,&fStack_a4,puVar6);
      SQRT__Wrapper_00406d50(auStack_24);
      iVar1 = *(int *)(param_1 + 0x18);
      fVar2 = _DAT_005d8568 - unaff_ESI * _DAT_005d8c68;
      *(float *)(iVar1 + 0x280) =
           (-fStack_1c - *(float *)(iVar1 + 0x118)) * fVar2 * _DAT_005d8cb8 +
           *(float *)(iVar1 + 0x280);
      uStack_94 = uStack_74;
      local_8c = fStack_6c;
      local_90 = uStack_70;
      local_88 = uStack_68;
      SQRT__Wrapper_00406d50(&uStack_94);
      iVar1 = *(int *)(param_1 + 0x18);
      *(float *)(iVar1 + 0x27c) =
           (local_8c * _DAT_005d85ec - *(float *)(iVar1 + 0x11c)) * fVar2 * _DAT_005d8cb8 +
           *(float *)(iVar1 + 0x27c);
    }
  }
  return;
}
