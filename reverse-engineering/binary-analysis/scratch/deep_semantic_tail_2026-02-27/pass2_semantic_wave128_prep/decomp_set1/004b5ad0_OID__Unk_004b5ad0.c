/* address: 0x004b5ad0 */
/* name: OID__Unk_004b5ad0 */
/* signature: int OID__Unk_004b5ad0(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int OID__Unk_004b5ad0(void)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float *pfVar4;
  int iVar5;
  float unaff_EBP;
  int iVar6;
  int iVar7;
  undefined4 *puVar8;
  undefined4 *puVar9;
  undefined4 **ppuVar10;
  float unaff_retaddr;
  float in_stack_00000004;
  float in_stack_00000008;
  float in_stack_00000014;
  float in_stack_00000018;
  float in_stack_0000001c;
  float in_stack_00000024;
  float in_stack_00000028;
  float in_stack_0000002c;
  float in_stack_00000034;
  float in_stack_00000038;
  float in_stack_0000003c;
  int in_stack_00000044;
  int *in_stack_00000048;
  undefined4 in_stack_0000004c;
  undefined4 in_stack_00000050;
  float in_stack_00000054;
  undefined4 *apuStack_ec [5];
  undefined4 *puStack_d8;
  undefined4 uStack_d4;
  undefined4 uStack_cc;
  undefined4 uStack_c8;
  float fStack_c4;
  undefined4 uStack_c0;
  undefined4 *puStack_bc;
  undefined4 *puStack_b8;
  undefined1 *puStack_b4;
  undefined4 *puStack_b0;
  float *pfStack_ac;
  float fStack_98;
  float fStack_94;
  float fStack_90;
  float fStack_8c;
  float local_88;
  float fStack_84;
  float fStack_80;
  undefined4 local_74 [5];
  undefined4 local_60 [10];
  undefined1 auStack_38 [52];
  float fStack_4;

  local_88 = in_stack_00000054;
  if ((*(int *)(in_stack_00000044 + 0x98) == 0) && (in_stack_00000048 != (int *)0x0)) {
    pfStack_ac = (float *)local_60;
    puStack_b0 = (undefined4 *)0x4b5b15;
    pfVar4 = (float *)(**(code **)(*in_stack_00000048 + 4))();
    fVar1 = pfVar4[2];
    fVar2 = pfVar4[1];
    fVar3 = *pfVar4;
    fStack_98 = unaff_retaddr * pfVar4[4] +
                in_stack_00000004 * pfVar4[5] + in_stack_00000008 * pfVar4[6];
    puStack_b0 = local_74;
    fStack_94 = unaff_retaddr * pfVar4[8] +
                in_stack_00000004 * pfVar4[9] + in_stack_00000008 * pfVar4[10];
    puStack_b4 = (undefined1 *)0x4b5b91;
    pfVar4 = (float *)(**(code **)*in_stack_00000048)();
    fStack_8c = unaff_EBP + *pfVar4;
    local_88 = unaff_retaddr * fVar3 + in_stack_00000004 * fVar2 + in_stack_00000008 * fVar1 +
               pfVar4[1];
    in_stack_00000004 = fStack_98 + pfVar4[2];
    in_stack_00000008 = fStack_80;
    puStack_b4 = auStack_38;
    puStack_b8 = (undefined4 *)0x4b5be9;
    fStack_84 = in_stack_00000004;
    fStack_4 = fStack_8c;
    pfVar4 = (float *)(**(code **)(*in_stack_00000048 + 4))();
    pfStack_ac = &fStack_98;
    fStack_98 = in_stack_00000024 * pfVar4[9] +
                in_stack_00000034 * pfVar4[10] + in_stack_00000014 * pfVar4[8];
    fStack_94 = in_stack_00000028 * pfVar4[9] +
                in_stack_00000038 * pfVar4[10] + in_stack_00000018 * pfVar4[8];
    fStack_90 = in_stack_0000002c * pfVar4[9] +
                in_stack_0000003c * pfVar4[10] + in_stack_0000001c * pfVar4[8];
    puStack_b0 = (undefined4 *)
                 (in_stack_0000002c * pfVar4[5] +
                 in_stack_0000003c * pfVar4[6] + in_stack_0000001c * pfVar4[4]);
    puStack_b4 = (undefined1 *)
                 (in_stack_00000028 * pfVar4[5] +
                 in_stack_00000038 * pfVar4[6] + in_stack_00000018 * pfVar4[4]);
    puStack_b8 = (undefined4 *)
                 (in_stack_00000024 * pfVar4[5] +
                 in_stack_00000014 * pfVar4[4] + in_stack_00000034 * pfVar4[6]);
    puStack_bc = (undefined4 *)0x4b5cdd;
    puStack_b0 = (undefined4 *)Vec3__SetXYZ();
    puStack_b4 = (undefined1 *)
                 (in_stack_0000002c * pfVar4[1] +
                 in_stack_0000003c * pfVar4[2] + in_stack_0000001c * *pfVar4);
    puStack_b8 = (undefined4 *)
                 (in_stack_00000028 * pfVar4[1] +
                 in_stack_00000038 * pfVar4[2] + in_stack_00000018 * *pfVar4);
    puStack_bc = (undefined4 *)
                 (in_stack_00000024 * pfVar4[1] +
                 in_stack_00000034 * pfVar4[2] + in_stack_00000014 * *pfVar4);
    uStack_c0 = 0x4b5d56;
    puStack_b4 = (undefined1 *)Vec3__SetXYZ();
    puStack_b8 = (undefined4 *)0x4b5d60;
    Mat34__SetRows();
    puVar8 = local_60;
    puVar9 = &stack0x00000014;
    for (iVar5 = 0xc; iVar5 != 0; iVar5 = iVar5 + -1) {
      *puVar9 = *puVar8;
      puVar8 = puVar8 + 1;
      puVar9 = puVar9 + 1;
    }
  }
  iVar7 = in_stack_00000044;
  pfStack_ac = &local_88;
  puStack_b0 = local_74;
  puStack_b8 = &stack0x00000014;
  puStack_bc = &stack0x00000004;
  fStack_c4 = 6.92124e-39;
  OID__Unk_004b5330();
  fStack_c4 = in_stack_00000054;
  uStack_c8 = in_stack_00000050;
  uStack_cc = in_stack_0000004c;
  puStack_d8 = &stack0x00000014;
  uStack_d4 = local_74[0];
  apuStack_ec[4] = &stack0x00000004;
  apuStack_ec[3] = (undefined4 *)0x4b5dcd;
  CMeshRenderer__RenderMesh();
  iVar5 = *(int *)(iVar7 + 0x90);
  iVar6 = 0;
  if (0 < iVar5) {
    do {
      pfStack_ac = (float *)in_stack_00000054;
      puStack_b0 = (undefined4 *)in_stack_00000050;
      puStack_b4 = (undefined1 *)in_stack_0000004c;
      puStack_bc = *(undefined4 **)(*(int *)(iVar7 + 0x94) + iVar6 * 4);
      puVar8 = &stack0x00000014;
      ppuVar10 = apuStack_ec;
      for (iVar5 = 0xc; iVar5 != 0; iVar5 = iVar5 + -1) {
        *ppuVar10 = (undefined4 *)*puVar8;
        puVar8 = puVar8 + 1;
        ppuVar10 = ppuVar10 + 1;
      }
      iVar5 = OID__Unk_004b5ad0();
      iVar6 = iVar6 + 1;
      iVar7 = in_stack_00000044;
    } while (iVar6 < *(int *)(in_stack_00000044 + 0x90));
  }
  return iVar5;
}
