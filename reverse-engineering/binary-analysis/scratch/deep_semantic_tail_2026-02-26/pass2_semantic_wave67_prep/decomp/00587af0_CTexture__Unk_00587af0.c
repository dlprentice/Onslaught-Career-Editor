/* address: 0x00587af0 */
/* name: CTexture__Unk_00587af0 */
/* signature: void __thiscall CTexture__Unk_00587af0(void * this, void * param_1, int param_2, int param_3, void * param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CTexture__Unk_00587af0(void *this,void *param_1,int param_2,int param_3,void *param_4)

{
  uint uVar1;
  void *extraout_EAX;
  uint uVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  undefined4 *puVar6;
  uint unaff_EDI;
  void *pvVar7;
  undefined2 in_FPUControlWord;
  undefined4 local_c;

  uVar1 = (int)param_1 + *(int *)((int)this + 0x103c);
  iVar4 = param_2 + *(int *)((int)this + 0x1048);
  if (*(int *)((int)this + 0x10e4) == 0) {
    iVar5 = *(int *)((int)this + 0x10d0);
    CFastVB__Helper_00426fd0(iVar5 << 8);
    if (extraout_EAX == (void *)0x0) {
      pvVar7 = (void *)0x0;
    }
    else {
      _vector_constructor_iterator_(extraout_EAX,0x10,iVar5 << 4,CFastVB__Helper_00574577);
      pvVar7 = extraout_EAX;
    }
    *(void **)((int)this + 0x10e4) = pvVar7;
    if (pvVar7 == (void *)0x0) {
      return;
    }
  }
  uVar2 = uVar1 & 0xfffffffc;
  if ((uVar2 != *(uint *)((int)this + 0x10dc)) || (iVar4 != *(int *)((int)this + 0x10e0))) {
    *(uint *)((int)this + 0x10dc) = uVar2;
    *(int *)((int)this + 0x10e0) = iVar4;
    uVar2 = *(uint *)((int)this + 0x10b8);
    iVar4 = *(int *)((int)this + 0x10e4);
    iVar5 = (*(uint *)((int)this + 0x10dc) >> 2) * *(int *)((int)this + 0x1058) +
            (uVar2 >> 2) * *(int *)((int)this + 0x107c) +
            *(int *)((int)this + 0x10e0) * *(int *)((int)this + 0x105c) + *(int *)((int)this + 0x20)
    ;
    for (; uVar2 < *(uint *)((int)this + 0x10c0); uVar2 = uVar2 + 4) {
      (**(code **)((int)this + 0x1080))(iVar4,iVar5);
      iVar5 = iVar5 + *(int *)((int)this + 0x107c);
      iVar4 = iVar4 + 0x100;
    }
  }
  iVar4 = *(int *)((int)this + 0x10bc);
  uVar2 = *(int *)((int)this + 0x1038) - *(int *)((int)this + 0x10b8);
  uVar3 = *(int *)((int)this + 0x1060) + uVar2;
  for (; iVar5 = param_3, uVar2 < uVar3; uVar2 = uVar2 + 1) {
    puVar6 = (undefined4 *)
             (((uVar2 & 0xfffffffc | uVar1 - iVar4 & 3) << 2 | uVar2 & 3) * 0x10 +
             *(int *)((int)this + 0x10e4));
    *(undefined4 *)param_3 = *puVar6;
    *(undefined4 *)(param_3 + 4) = puVar6[1];
    *(undefined4 *)(param_3 + 8) = puVar6[2];
    *(undefined4 *)(param_3 + 0xc) = puVar6[3];
    param_3 = param_3 + 0x10;
  }
  if (*(int *)((int)this + 0x18) != 0) {
    local_c = CONCAT22(local_c._2_2_,in_FPUControlWord);
    DAT_009d0c58 = local_c;
    for (param_3 = param_3 + *(int *)((int)this + 0x1060) * -0x10; (uint)param_3 < (uint)iVar5;
        param_3 = param_3 + 0x10) {
      if (((((float)(int)ROUND(*(float *)param_3 * _DAT_005e9f00 + _DAT_005e72d4) * _DAT_005e9efc ==
             *(float *)((int)this + 0x24)) &&
           ((float)(int)ROUND(*(float *)(param_3 + 4) * _DAT_005e9ef8 + _DAT_005e72d4) *
            _DAT_005e9ef4 == *(float *)((int)this + 0x28))) &&
          ((float)(int)ROUND(*(float *)(param_3 + 8) * _DAT_005e9f00 + _DAT_005e72d4) *
           _DAT_005e9efc == *(float *)((int)this + 0x2c))) &&
         ((float)(int)ROUND(*(float *)((int)this + 0x1074) * *(float *)(param_3 + 0xc) +
                            _DAT_005e72d4) * *(float *)((int)this + 0x1078) ==
          *(float *)((int)this + 0x30))) {
        *(undefined4 *)param_3 = 0;
        *(undefined4 *)(param_3 + 4) = 0;
        *(undefined4 *)(param_3 + 8) = 0;
        *(undefined4 *)(param_3 + 0xc) = 0;
      }
    }
  }
  if (*(int *)((int)this + 0x10) != 0) {
    CTexture__Helper_0058210e(this,param_3 + *(int *)((int)this + 0x1060) * -0x10,unaff_EDI);
  }
  return;
}
