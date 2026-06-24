/* address: 0x004f3ac0 */
/* name: CUnitAI__GetWorldPositionForTargeting */
/* signature: void __thiscall CUnitAI__GetWorldPositionForTargeting(void * this, int param_1, void * param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CUnitAI__GetWorldPositionForTargeting(void *this,int param_1,void *param_2)

{
  undefined4 uVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  float fVar6;
  float fVar7;
  float fVar8;
  float fVar9;
  float fVar10;
  float fVar11;
  float fVar12;
  float fVar13;
  float fVar14;
  float fVar15;
  uint uVar16;
  int iVar17;
  float *pfVar18;
  float *pfVar19;
  undefined4 uStack_14;

  uVar16 = *(uint *)((int)this + 0x34);
  if ((uVar16 & 0x80100) == 0) {
    if ((uVar16 & 8) == 0) {
      if (*(int **)((int)this + 0x30) != (int *)0x0) {
        iVar17 = (**(code **)(**(int **)((int)this + 0x30) + 0x10))();
        if (iVar17 != 0) {
          uVar1 = *(undefined4 *)((int)this + 0x20);
          fVar2 = *(float *)(iVar17 + 8);
          fVar3 = *(float *)((int)this + 0x24);
          *(undefined4 *)param_1 = *(undefined4 *)((int)this + 0x1c);
          *(undefined4 *)(param_1 + 4) = uVar1;
          *(float *)(param_1 + 8) = fVar2 + fVar3;
          *(undefined4 *)(param_1 + 0xc) = uStack_14;
          return;
        }
      }
    }
    else if ((uVar16 & 0x200) != 0) {
      *(undefined4 *)param_1 = *(undefined4 *)((int)this + 0x1c);
      *(undefined4 *)(param_1 + 4) = *(undefined4 *)((int)this + 0x20);
      *(undefined4 *)(param_1 + 8) = *(undefined4 *)((int)this + 0x24);
      *(undefined4 *)(param_1 + 0xc) = *(undefined4 *)((int)this + 0x28);
      *(float *)(param_1 + 8) = *(float *)(param_1 + 8) + _DAT_005df704;
      return;
    }
  }
  else if (*(int **)((int)this + 0x30) != (int *)0x0) {
    iVar17 = (**(code **)(**(int **)((int)this + 0x30) + 0x10))();
    if (iVar17 != 0) {
      pfVar19 = (float *)((int)this + 0x3c);
      if ((*(uint *)((int)this + 0x34) & 0x80000000) == 0) {
        pfVar19 = (float *)&DAT_0083d9c0;
      }
      pfVar18 = (float *)(**(code **)(**(int **)((int)this + 0x30) + 0x10))();
      fVar2 = pfVar19[6];
      fVar3 = pfVar18[2];
      fVar4 = pfVar19[5];
      fVar5 = pfVar18[1];
      fVar6 = pfVar19[4];
      fVar7 = *pfVar18;
      fVar8 = pfVar19[10];
      fVar9 = pfVar18[2];
      fVar10 = pfVar19[9];
      fVar11 = pfVar18[1];
      fVar12 = pfVar19[8];
      fVar13 = *pfVar18;
      fVar14 = *(float *)((int)this + 0x20);
      fVar15 = *(float *)((int)this + 0x24);
      *(float *)param_1 =
           *pfVar19 * *pfVar18 + pfVar19[1] * pfVar18[1] + pfVar19[2] * pfVar18[2] +
           *(float *)((int)this + 0x1c);
      *(float *)(param_1 + 4) = fVar6 * fVar7 + fVar4 * fVar5 + fVar2 * fVar3 + fVar14;
      *(float *)(param_1 + 8) = fVar12 * fVar13 + fVar10 * fVar11 + fVar8 * fVar9 + fVar15;
      *(undefined4 *)(param_1 + 0xc) = uStack_14;
      return;
    }
  }
  *(undefined4 *)param_1 = *(undefined4 *)((int)this + 0x1c);
  *(undefined4 *)(param_1 + 4) = *(undefined4 *)((int)this + 0x20);
  *(undefined4 *)(param_1 + 8) = *(undefined4 *)((int)this + 0x24);
  *(undefined4 *)(param_1 + 0xc) = *(undefined4 *)((int)this + 0x28);
  return;
}
