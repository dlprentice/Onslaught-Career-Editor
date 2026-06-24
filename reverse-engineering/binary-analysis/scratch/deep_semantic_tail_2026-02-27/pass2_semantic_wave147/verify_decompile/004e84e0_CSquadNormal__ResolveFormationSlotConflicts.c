/* address: 0x004e84e0 */
/* name: CSquadNormal__ResolveFormationSlotConflicts */
/* signature: int __fastcall CSquadNormal__ResolveFormationSlotConflicts(int param_1) */


int __fastcall CSquadNormal__ResolveFormationSlotConflicts(int param_1)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  int iVar3;
  float fVar4;
  float fVar5;
  void *extraout_EAX;
  void *extraout_EAX_00;
  int iVar6;
  void *extraout_EAX_01;
  int *piVar7;
  void *this;
  void *unaff_EDI;
  int local_cc;
  float local_c8;
  float local_b0;
  float local_ac;
  float local_a0;
  float local_9c;
  undefined4 local_90;
  undefined4 local_8c;
  undefined4 local_88;
  undefined1 local_80 [16];
  undefined4 local_70;
  undefined4 local_6c;
  undefined4 local_68;
  undefined4 local_60;
  undefined4 local_5c;
  undefined4 local_58;
  undefined1 local_50 [16];
  float local_40;
  float local_3c;
  undefined1 local_30 [16];
  undefined1 local_20 [16];
  undefined1 local_10 [16];

  local_cc = 1;
  puVar1 = *(undefined4 **)(param_1 + 0xa4);
  if (puVar1 == (undefined4 *)0x0) {
    this = (void *)0x0;
  }
  else {
    this = (void *)*puVar1;
  }
  while (this != (void *)0x0) {
    local_90 = *(undefined4 *)((int)this + 4);
    iVar6 = *(int *)((int)this + 0x10);
    local_8c = *(undefined4 *)((int)this + 8);
    local_88 = 0;
    CSquadNormal__Helper_0040d2c0((void *)(iVar6 + 0x3c),local_20,&local_90,unaff_EDI);
    Vec3__Add((void *)(iVar6 + 0x1c),local_50,extraout_EAX,unaff_EDI);
    Vec3__SetXYZ();
    puVar2 = *(undefined4 **)(param_1 + 0xa4);
    local_c8 = SQRT(local_b0 * local_b0 + local_ac * local_ac);
    if (puVar2 == (undefined4 *)0x0) {
      piVar7 = (int *)0x0;
    }
    else {
      piVar7 = (int *)*puVar2;
    }
    while (piVar7 != (int *)0x0) {
      local_60 = *(undefined4 *)((int)this + 4);
      iVar6 = *(int *)((int)this + 0x10);
      iVar3 = *piVar7;
      local_5c = *(undefined4 *)((int)this + 8);
      local_58 = 0;
      CSquadNormal__Helper_0040d2c0((void *)(iVar6 + 0x3c),local_30,&local_60,unaff_EDI);
      Vec3__Add((void *)(iVar6 + 0x1c),&local_40,extraout_EAX_00,unaff_EDI);
      fVar4 = local_40 - *(float *)(iVar3 + 0x1c);
      fVar5 = local_3c - *(float *)(iVar3 + 0x20);
      if ((SQRT(fVar4 * fVar4 + fVar5 * fVar5) < local_c8) &&
         (iVar6 = CSquadNormal__Helper_004e97e0(this,piVar7,unaff_EDI), iVar6 != 0)) {
        local_70 = *(undefined4 *)((int)this + 4);
        iVar6 = *(int *)((int)this + 0x10);
        local_6c = *(undefined4 *)((int)this + 8);
        local_68 = 0;
        CSquadNormal__Helper_0040d2c0((void *)(iVar6 + 0x3c),local_10,&local_70,unaff_EDI);
        Vec3__Add((void *)(iVar6 + 0x1c),local_80,extraout_EAX_01,unaff_EDI);
        Vec3__SetXYZ();
        local_cc = 0;
        local_c8 = SQRT(local_a0 * local_a0 + local_9c * local_9c);
      }
      puVar2 = (undefined4 *)puVar2[1];
      if (puVar2 == (undefined4 *)0x0) {
        piVar7 = (int *)0x0;
      }
      else {
        piVar7 = (int *)*puVar2;
      }
    }
    puVar1 = (undefined4 *)puVar1[1];
    if (puVar1 == (undefined4 *)0x0) {
      this = (void *)0x0;
    }
    else {
      this = (void *)*puVar1;
    }
  }
  return local_cc;
}
