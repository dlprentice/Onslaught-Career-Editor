/* address: 0x004e7cf0 */
/* name: CSquadNormal__Unk_004e7cf0 */
/* signature: int __fastcall CSquadNormal__Unk_004e7cf0(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __fastcall CSquadNormal__Unk_004e7cf0(int param_1)

{
  undefined4 *puVar1;
  float fVar2;
  float fVar3;
  void *pvVar4;
  void *extraout_EAX;
  void *extraout_EAX_00;
  uint uVar5;
  int iVar6;
  int *piVar7;
  void *unaff_EDI;
  float10 fVar8;
  int local_80;
  int local_78;
  int iStack_60;
  int iStack_5c;
  undefined4 uStack_58;
  float local_50;
  float local_4c;
  float fStack_40;
  float fStack_3c;
  undefined1 local_20 [16];
  undefined1 auStack_10 [16];

  *(undefined4 *)(param_1 + 0x108) = *(undefined4 *)(param_1 + 0x10c);
  if (*(int *)(param_1 + 0x120) != 4) {
    if (*(int *)(param_1 + 0x80) != 0) {
      return 0;
    }
    if (DAT_00672fd0 <= *(float *)(param_1 + 0x11c) + _DAT_005d85d8) {
      puVar1 = *(undefined4 **)(param_1 + 0xa4);
      local_80 = 0;
      if (puVar1 == (undefined4 *)0x0) {
        piVar7 = (int *)0x0;
      }
      else {
        piVar7 = (int *)*puVar1;
      }
      while (piVar7 != (int *)0x0) {
        if (*piVar7 != 0) {
          iVar6 = piVar7[4];
          pvVar4 = (void *)Vec3__SetXYZ();
          CSquadNormal__Helper_0040d2c0((void *)(piVar7[4] + 0x3c),local_20,pvVar4,unaff_EDI);
          Vec3__Add((void *)(iVar6 + 0x1c),&local_50,extraout_EAX,unaff_EDI);
          fVar2 = *(float *)(*piVar7 + 0x1c) - local_50;
          fVar3 = *(float *)(*piVar7 + 0x20) - local_4c;
          (**(code **)(*(int *)piVar7[4] + 0x138))();
          fVar8 = (float10)(**(code **)(*(int *)piVar7[4] + 0x138))();
          if (fVar8 * (float10)_DAT_005df260 <
              SQRT((float10)fVar2 * (float10)fVar2 + (float10)fVar3 * (float10)fVar3)) {
            if ((*piVar7 != 0) && (iVar6 = piVar7[4], *(int *)(iVar6 + 0xd0) != 0)) {
              iStack_60 = piVar7[1];
              iStack_5c = piVar7[2];
              uStack_58 = 0;
              CSquadNormal__Helper_0040d2c0((void *)(iVar6 + 0x3c),auStack_10,&iStack_60,unaff_EDI);
              Vec3__Add((void *)(iVar6 + 0x1c),&fStack_40,extraout_EAX_00,unaff_EDI);
              local_78 = (int)(longlong)ROUND(fStack_40);
              uVar5 = local_78 >> 1;
              iVar6 = local_78 >> 4;
              local_78 = (int)(longlong)ROUND(fStack_3c);
              uVar5 = uVar5 & 0x80000007;
              if ((int)uVar5 < 0) {
                uVar5 = (uVar5 - 1 | 0xfffffff8) + 1;
              }
              if ((*(byte *)(iVar6 * 0x100 + (local_78 >> 1) + *(int *)(piVar7[4] + 0xd0)) &
                  (byte)(1 << ((byte)uVar5 & 0x1f))) == 0) goto LAB_004e7ea8;
            }
            local_80 = local_80 + 1;
          }
        }
LAB_004e7ea8:
        puVar1 = (undefined4 *)puVar1[1];
        if (puVar1 == (undefined4 *)0x0) {
          piVar7 = (int *)0x0;
        }
        else {
          piVar7 = (int *)*puVar1;
        }
      }
      if (*(int *)(param_1 + 0xb4) == 0) {
        return 0;
      }
      fVar2 = _DAT_005d8568 - ((float)local_80 / (float)*(int *)(param_1 + 0xb4)) * _DAT_005d8bd8;
      if (fVar2 < _DAT_005d856c) {
        fVar2 = _DAT_005d856c;
      }
      *(float *)(param_1 + 0x108) = fVar2 * *(float *)(param_1 + 0x108);
      if (fVar2 <= _DAT_005d85ec) {
        return 0;
      }
    }
    *(float *)(param_1 + 0x11c) = DAT_00672fd0;
  }
  return 1;
}
