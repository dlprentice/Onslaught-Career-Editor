/* address: 0x005888bc */
/* name: CFastVB__Unk_005888bc */
/* signature: int CFastVB__Unk_005888bc(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CFastVB__Unk_005888bc(void)

{
  int *piVar1;
  float fVar2;
  float *pfVar3;
  int iVar4;
  uint uVar5;
  int *piVar6;
  int *piVar7;
  int *piVar8;
  uint uVar9;
  float *pfVar10;
  undefined4 *puVar11;
  undefined4 *puVar12;
  int in_stack_00000004;
  int in_stack_00000008;
  int in_stack_0000000c;
  float *in_stack_00000010;
  int *in_stack_00000014;
  int in_stack_00000018;
  int *in_stack_0000001c;
  int *in_stack_00000020;
  int *in_stack_00000024;
  undefined4 *in_stack_00000028;
  float *in_stack_0000002c;
  int in_stack_00000030;
  float local_344 [195];
  uint local_38;
  int local_34;
  int local_30;
  float local_2c;
  float local_28;
  float local_24;
  float local_20;
  float local_1c;
  float local_18;
  float local_14;
  float local_10;
  float local_c;
  undefined4 *local_8;

  local_8 = (undefined4 *)(in_stack_0000000c + (int)in_stack_00000028);
  piVar8 = (int *)(in_stack_00000018 - (int)in_stack_00000028);
  if (in_stack_00000008 == 0) {
    in_stack_00000008 = in_stack_00000004;
  }
  if (in_stack_00000024 == (int *)0x1) {
    piVar6 = (int *)0x0;
    if (in_stack_00000014 != (int *)0x0) {
      in_stack_00000024 = in_stack_00000014;
      in_stack_00000028 = (undefined4 *)((int)in_stack_00000010 + (int)in_stack_00000028);
      do {
        local_14 = 0.0;
        local_10 = 0.0;
        local_c = 0.0;
        local_344[0] = 0.0;
        local_344[1] = 0.0;
        local_344[2] = 0.0;
        if (DAT_005e6a3c <= *in_stack_0000002c) {
          do {
            uVar5 = __ftol();
            fVar2 = (float)(int)(uVar5 & 0xfffffffe);
            if ((int)(uVar5 & 0xfffffffe) < 0) {
              fVar2 = fVar2 + _DAT_005e72d8;
            }
            fVar2 = *in_stack_0000002c - fVar2;
            CDXEngine__Helper_00576161();
            CFastVB__Helper_0057618b();
            in_stack_0000002c = in_stack_0000002c + 1;
            local_2c = local_2c * fVar2;
            local_28 = local_28 * fVar2;
            local_24 = local_24 * fVar2;
            local_20 = local_20 * fVar2;
            local_1c = local_1c * fVar2;
            local_18 = local_18 * fVar2;
            local_14 = local_2c + local_14;
            local_10 = local_28 + local_10;
            local_c = local_24 + local_c;
            local_344[0] = local_20 + local_344[0];
            local_344[1] = local_1c + local_344[1];
            local_344[2] = local_18 + local_344[2];
          } while (DAT_005e6a3c <= *in_stack_0000002c);
        }
        if (in_stack_00000030 == 0) {
          *in_stack_00000010 = local_14;
          in_stack_00000010[1] = local_10;
          in_stack_00000010[2] = local_c;
          pfVar10 = (float *)*in_stack_00000020;
          *pfVar10 = local_344[0];
          pfVar10[1] = local_344[1];
          pfVar10[2] = local_344[2];
          puVar11 = local_8;
          puVar12 = in_stack_00000028;
          for (uVar5 = (uint)piVar8 >> 2; uVar5 != 0; uVar5 = uVar5 - 1) {
            *puVar12 = *puVar11;
            puVar11 = puVar11 + 1;
            puVar12 = puVar12 + 1;
          }
          for (uVar5 = (uint)piVar8 & 3; uVar5 != 0; uVar5 = uVar5 - 1) {
            *(undefined1 *)puVar12 = *(undefined1 *)puVar11;
            puVar11 = (undefined4 *)((int)puVar11 + 1);
            puVar12 = (undefined4 *)((int)puVar12 + 1);
          }
        }
        else {
          puVar11 = local_8;
          puVar12 = in_stack_00000028;
          for (uVar5 = (uint)piVar8 >> 2; uVar5 != 0; uVar5 = uVar5 - 1) {
            *puVar12 = *puVar11;
            puVar11 = puVar11 + 1;
            puVar12 = puVar12 + 1;
          }
          for (uVar5 = (uint)piVar8 & 3; uVar5 != 0; uVar5 = uVar5 - 1) {
            *(undefined1 *)puVar12 = *(undefined1 *)puVar11;
            puVar11 = (undefined4 *)((int)puVar11 + 1);
            puVar12 = (undefined4 *)((int)puVar12 + 1);
          }
          *in_stack_00000010 = local_14;
          in_stack_00000010[1] = local_10;
          in_stack_00000010[2] = local_c;
          pfVar10 = (float *)*in_stack_00000020;
          *pfVar10 = local_344[0];
          pfVar10[1] = local_344[1];
          pfVar10[2] = local_344[2];
        }
        *in_stack_00000020 = *in_stack_00000020 + in_stack_00000018;
        in_stack_00000028 = (undefined4 *)((int)in_stack_00000028 + in_stack_00000018);
        local_8 = (undefined4 *)((int)local_8 + in_stack_00000018);
        in_stack_00000010 = (float *)((int)in_stack_00000010 + in_stack_00000018);
        *in_stack_0000001c = *in_stack_0000001c + in_stack_00000018;
        in_stack_0000002c = in_stack_0000002c + 1;
        in_stack_00000024 = (int *)((int)in_stack_00000024 + -1);
        piVar6 = in_stack_0000001c;
      } while (in_stack_00000024 != (int *)0x0);
    }
  }
  else {
    piVar6 = in_stack_00000024;
    if (in_stack_00000014 != (int *)0x0) {
      local_38 = (int)in_stack_00000024 * 0xc;
      local_30 = (int)in_stack_00000014;
      in_stack_00000028 = (undefined4 *)((int)in_stack_00000010 + (int)in_stack_00000028);
      do {
        uVar5 = local_38;
        local_14 = 0.0;
        local_10 = 0.0;
        pfVar10 = local_344;
        for (uVar9 = local_38 >> 2; uVar9 != 0; uVar9 = uVar9 - 1) {
          *pfVar10 = 0.0;
          pfVar10 = pfVar10 + 1;
        }
        local_c = 0.0;
        fVar2 = *in_stack_0000002c;
        for (uVar5 = uVar5 & 3; uVar5 != 0; uVar5 = uVar5 - 1) {
          *(undefined1 *)pfVar10 = 0;
          pfVar10 = (float *)((int)pfVar10 + 1);
        }
        if (DAT_005e6a3c <= fVar2) {
          do {
            uVar5 = __ftol();
            iVar4 = (uVar5 >> 1) * 2;
            fVar2 = (float)iVar4;
            if (iVar4 < 0) {
              fVar2 = fVar2 + _DAT_005e72d8;
            }
            fVar2 = *in_stack_0000002c - fVar2;
            CDXEngine__Helper_00576161();
            local_20 = local_20 * fVar2;
            in_stack_00000014 = (int *)0x0;
            local_1c = local_1c * fVar2;
            local_18 = local_18 * fVar2;
            local_14 = local_20 + local_14;
            local_10 = local_1c + local_10;
            local_c = local_18 + local_c;
            if (in_stack_00000024 != (int *)0x0) {
              local_34 = (uVar5 >> 1) * 0x40 + in_stack_00000008;
              pfVar10 = local_344 + 2;
              do {
                CFastVB__Helper_0057618b();
                local_2c = local_2c * fVar2;
                in_stack_00000014 = (int *)((int)in_stack_00000014 + 1);
                local_28 = local_28 * fVar2;
                local_24 = local_24 * fVar2;
                pfVar10[-2] = local_2c + pfVar10[-2];
                pfVar10[-1] = local_28 + pfVar10[-1];
                *pfVar10 = local_24 + *pfVar10;
                pfVar10 = pfVar10 + 3;
              } while (in_stack_00000014 < in_stack_00000024);
            }
            in_stack_0000002c = in_stack_0000002c + 1;
          } while (DAT_005e6a3c <= *in_stack_0000002c);
        }
        piVar6 = piVar8;
        if (in_stack_00000030 == 0) {
          *in_stack_00000010 = local_14;
          in_stack_00000010[1] = local_10;
          in_stack_00000010[2] = local_c;
          if (in_stack_00000024 != (int *)0x0) {
            pfVar10 = local_344;
            in_stack_00000014 = in_stack_00000024;
            piVar7 = in_stack_00000020;
            do {
              pfVar3 = (float *)*piVar7;
              *pfVar3 = *pfVar10;
              pfVar3[1] = pfVar10[1];
              pfVar3[2] = pfVar10[2];
              *piVar7 = *piVar7 + in_stack_00000018;
              piVar1 = (int *)((int)piVar7 + ((int)in_stack_0000001c - (int)in_stack_00000020));
              *piVar1 = *piVar1 + in_stack_00000018;
              pfVar10 = pfVar10 + 3;
              piVar7 = piVar7 + 1;
              in_stack_00000014 = (int *)((int)in_stack_00000014 + -1);
            } while (in_stack_00000014 != (int *)0x0);
          }
          puVar11 = local_8;
          puVar12 = in_stack_00000028;
          for (uVar5 = (uint)piVar8 >> 2; uVar5 != 0; uVar5 = uVar5 - 1) {
            *puVar12 = *puVar11;
            puVar11 = puVar11 + 1;
            puVar12 = puVar12 + 1;
          }
          for (uVar5 = (uint)piVar8 & 3; uVar5 != 0; uVar5 = uVar5 - 1) {
            *(undefined1 *)puVar12 = *(undefined1 *)puVar11;
            puVar11 = (undefined4 *)((int)puVar11 + 1);
            puVar12 = (undefined4 *)((int)puVar12 + 1);
          }
        }
        else {
          puVar11 = local_8;
          puVar12 = in_stack_00000028;
          for (uVar5 = (uint)piVar8 >> 2; uVar5 != 0; uVar5 = uVar5 - 1) {
            *puVar12 = *puVar11;
            puVar11 = puVar11 + 1;
            puVar12 = puVar12 + 1;
          }
          for (uVar5 = (uint)piVar8 & 3; uVar5 != 0; uVar5 = uVar5 - 1) {
            *(undefined1 *)puVar12 = *(undefined1 *)puVar11;
            puVar11 = (undefined4 *)((int)puVar11 + 1);
            puVar12 = (undefined4 *)((int)puVar12 + 1);
          }
          *in_stack_00000010 = local_14;
          in_stack_00000010[1] = local_10;
          in_stack_00000010[2] = local_c;
          if (in_stack_00000024 != (int *)0x0) {
            pfVar10 = local_344;
            in_stack_00000014 = in_stack_00000024;
            piVar6 = in_stack_00000020;
            do {
              pfVar3 = (float *)*piVar6;
              *pfVar3 = *pfVar10;
              pfVar3[1] = pfVar10[1];
              pfVar3[2] = pfVar10[2];
              *piVar6 = *piVar6 + in_stack_00000018;
              piVar7 = (int *)(((int)in_stack_0000001c - (int)in_stack_00000020) + (int)piVar6);
              *piVar7 = *piVar7 + in_stack_00000018;
              pfVar10 = pfVar10 + 3;
              piVar6 = piVar6 + 1;
              in_stack_00000014 = (int *)((int)in_stack_00000014 + -1);
            } while (in_stack_00000014 != (int *)0x0);
          }
        }
        in_stack_00000028 = (undefined4 *)((int)in_stack_00000028 + in_stack_00000018);
        local_8 = (undefined4 *)((int)local_8 + in_stack_00000018);
        in_stack_00000010 = (float *)((int)in_stack_00000010 + in_stack_00000018);
        in_stack_0000002c = in_stack_0000002c + 1;
        local_30 = local_30 + -1;
      } while (local_30 != 0);
    }
  }
  return (int)piVar6;
}
