/* address: 0x00581a4f */
/* name: CFastVB__TexelUnpackProfile__ctorFromDescriptor */
/* signature: int CFastVB__TexelUnpackProfile__ctorFromDescriptor(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CFastVB__TexelUnpackProfile__ctorFromDescriptor(void)

{
  int *piVar1;
  float fVar2;
  undefined4 *puVar3;
  undefined4 *in_ECX;
  int iVar4;
  undefined *puVar5;
  float *pfVar6;
  uint uVar7;
  uint uVar8;
  undefined4 *puVar9;
  undefined4 *in_stack_00000004;
  uint in_stack_00000008;
  int in_stack_0000000c;

  *in_ECX = &PTR_CFastVB__TexelUnpackProfile_scalar_deleting_dtor_005e9ed0;
  _vector_constructor_iterator_(in_ECX + 0xe,0x10,0x100,CFastVB__ReturnInputInt);
  in_ECX[8] = *in_stack_00000004;
  in_ECX[1] = in_stack_00000004[1];
  in_ECX[0x416] = in_stack_00000004[2];
  in_ECX[0x417] = in_stack_00000004[3];
  puVar3 = in_stack_00000004 + 10;
  puVar9 = in_ECX + 0x40e;
  for (iVar4 = 6; iVar4 != 0; iVar4 = iVar4 + -1) {
    *puVar9 = *puVar3;
    puVar3 = puVar3 + 1;
    puVar9 = puVar9 + 1;
  }
  puVar5 = &DAT_00657a00;
  if (in_stack_00000004[0x10] == 0) {
    puVar5 = &DAT_00657980;
  }
  in_ECX[0xd] = puVar5;
  fVar2 = _DAT_005e9ee0;
  in_ECX[0x41c] = in_stack_00000008 >> 3;
  in_ECX[0x414] = 0;
  in_ECX[0x415] = 0;
  in_ECX[3] = (uint)(in_stack_00000008 != 0);
  in_ECX[2] = in_stack_0000000c;
  in_ECX[6] = in_stack_00000004[0x12];
  in_ECX[4] = in_stack_00000004[0x11];
  in_ECX[5] = 0;
  if (in_ECX[6] != 0) {
    uVar7 = in_stack_00000004[0x12];
    in_ECX[9] = (float)(uVar7 >> 0x10 & 0xff) * fVar2;
    in_ECX[10] = (float)(uVar7 >> 8 & 0xff) * fVar2;
    in_ECX[0xb] = (float)(uVar7 & 0xff) * fVar2;
    in_ECX[0xc] = (float)(uVar7 >> 0x18) * fVar2;
  }
  if (in_stack_0000000c == 2) {
    if (in_ECX[1] == 0x3d) goto LAB_00581b66;
    in_ECX[4] = 0;
  }
  if (in_stack_0000000c == 3) {
    in_ECX[4] = 0;
  }
LAB_00581b66:
  if ((in_ECX[1] == 0x29) || (in_ECX[1] == 0x28)) {
    in_ECX[7] = 1;
    if (in_stack_00000004[0x13] == 0) {
      iVar4 = 0x100;
      puVar3 = in_ECX + 0x10;
      do {
        puVar3[1] = 0x3f800000;
        *puVar3 = 0x3f800000;
        iVar4 = iVar4 + -1;
        puVar3[-1] = 0x3f800000;
        puVar3[-2] = 0x3f800000;
        puVar3 = puVar3 + 4;
      } while (iVar4 != 0);
    }
    else {
      pfVar6 = (float *)(in_ECX + 0xf);
      uVar7 = 0;
      do {
        uVar8 = uVar7 + 4;
        pfVar6[-1] = (float)*(byte *)(uVar7 + in_stack_00000004[0x13]) * fVar2;
        *pfVar6 = (float)*(byte *)(uVar7 + 1 + in_stack_00000004[0x13]) * fVar2;
        pfVar6[1] = (float)*(byte *)(uVar7 + 2 + in_stack_00000004[0x13]) * fVar2;
        pfVar6[2] = (float)*(byte *)(uVar7 + 3 + in_stack_00000004[0x13]) * fVar2;
        pfVar6 = pfVar6 + 4;
        uVar7 = uVar8;
      } while (uVar8 < 0x400);
    }
  }
  else {
    in_ECX[7] = 0;
  }
  piVar1 = in_ECX + 0x40e;
  in_ECX[0x419] = in_ECX[0x411] - in_ECX[0x40f];
  in_ECX[0x41a] = in_ECX[0x413] - in_ECX[0x412];
  in_ECX[0x418] = in_ECX[0x410] - *piVar1;
  in_ECX[0x41b] = in_ECX[0x41c] * (in_ECX[0x410] - *piVar1);
  if (in_ECX[3] != 0) {
    in_ECX[8] = in_ECX[8] +
                in_ECX[0x41c] * *piVar1 + in_ECX[0x416] * in_ECX[0x40f] +
                in_ECX[0x417] * in_ECX[0x412];
    in_ECX[0x410] = in_ECX[0x418];
    in_ECX[0x411] = in_ECX[0x419];
    *piVar1 = 0;
    in_ECX[0x40f] = 0;
    in_ECX[0x412] = 0;
    in_ECX[0x413] = in_ECX[0x41a];
  }
  return (int)in_ECX;
}
