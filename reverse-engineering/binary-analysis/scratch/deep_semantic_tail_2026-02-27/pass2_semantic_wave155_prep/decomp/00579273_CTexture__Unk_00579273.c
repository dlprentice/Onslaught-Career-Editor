/* address: 0x00579273 */
/* name: CTexture__Unk_00579273 */
/* signature: int CTexture__Unk_00579273(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CTexture__Unk_00579273(void)

{
  undefined4 uVar1;
  undefined4 *in_stack_00000004;
  float *in_stack_00000008;
  int in_stack_0000000c;
  undefined4 *in_stack_00000010;
  float *in_stack_00000014;
  int in_stack_00000018;
  float *in_stack_0000001c;

  if (in_stack_00000010 == (undefined4 *)0x0) {
    in_stack_00000004[0xe] = 0;
    in_stack_00000004[0xd] = 0;
    in_stack_00000004[0xc] = 0;
    in_stack_00000004[0xb] = 0;
    in_stack_00000004[9] = 0;
    in_stack_00000004[8] = 0;
    in_stack_00000004[7] = 0;
    in_stack_00000004[6] = 0;
    in_stack_00000004[4] = 0;
    in_stack_00000004[3] = 0;
    in_stack_00000004[2] = 0;
    in_stack_00000004[1] = 0;
    in_stack_00000004[0xf] = 0x3f800000;
    in_stack_00000004[10] = 0x3f800000;
    in_stack_00000004[5] = 0x3f800000;
    *in_stack_00000004 = 0x3f800000;
  }
  else if (in_stack_0000000c == 0) {
    in_stack_00000004[0xe] = 0;
    in_stack_00000004[0xd] = 0;
    in_stack_00000004[0xc] = 0;
    in_stack_00000004[0xb] = 0;
    in_stack_00000004[9] = 0;
    in_stack_00000004[8] = 0;
    in_stack_00000004[7] = 0;
    in_stack_00000004[6] = 0;
    in_stack_00000004[4] = 0;
    in_stack_00000004[3] = 0;
    in_stack_00000004[2] = 0;
    in_stack_00000004[1] = 0;
    *in_stack_00000004 = *in_stack_00000010;
    in_stack_00000004[5] = in_stack_00000010[1];
    uVar1 = in_stack_00000010[2];
    in_stack_00000004[0xf] = 0x3f800000;
    in_stack_00000004[10] = uVar1;
  }
  else {
    CTexture__Helper_005775bd();
    if (in_stack_00000008 == (float *)0x0) {
      CVertexShader__Helper_00576b47();
      CTexture__Helper_005768fe();
      CTexture__Helper_005768fe();
    }
    else {
      CVertexShader__Helper_00576b47();
      in_stack_00000004[0xe] = 0;
      in_stack_00000004[0xd] = 0;
      in_stack_00000004[0xc] = 0;
      in_stack_00000004[0xb] = 0;
      in_stack_00000004[9] = 0;
      in_stack_00000004[8] = 0;
      in_stack_00000004[7] = 0;
      in_stack_00000004[6] = 0;
      in_stack_00000004[4] = 0;
      in_stack_00000004[3] = 0;
      in_stack_00000004[2] = 0;
      in_stack_00000004[1] = 0;
      in_stack_00000004[0xf] = 0x3f800000;
      in_stack_00000004[10] = 0x3f800000;
      in_stack_00000004[5] = 0x3f800000;
      *in_stack_00000004 = 0x3f800000;
      in_stack_00000004[0xc] = -*in_stack_00000008;
      in_stack_00000004[0xd] = -in_stack_00000008[1];
      in_stack_00000004[0xe] = -in_stack_00000008[2];
      CTexture__Helper_005768fe();
      CTexture__Helper_005768fe();
      CTexture__Helper_005768fe();
      in_stack_00000004[0xc] = (float)in_stack_00000004[0xc] + *in_stack_00000008;
      in_stack_00000004[0xd] = in_stack_00000008[1] + (float)in_stack_00000004[0xd];
      in_stack_00000004[0xe] = (float)in_stack_00000004[0xe] + in_stack_00000008[2];
    }
  }
  if (in_stack_00000018 != 0) {
    CTexture__Helper_005775bd();
    if (in_stack_00000014 == (float *)0x0) {
      CTexture__Helper_005768fe();
    }
    else {
      in_stack_00000004[0xc] = (float)in_stack_00000004[0xc] - *in_stack_00000014;
      in_stack_00000004[0xd] = (float)in_stack_00000004[0xd] - in_stack_00000014[1];
      in_stack_00000004[0xe] = (float)in_stack_00000004[0xe] - in_stack_00000014[2];
      CTexture__Helper_005768fe();
      in_stack_00000004[0xc] = (float)in_stack_00000004[0xc] + *in_stack_00000014;
      in_stack_00000004[0xd] = (float)in_stack_00000004[0xd] + in_stack_00000014[1];
      in_stack_00000004[0xe] = (float)in_stack_00000004[0xe] + in_stack_00000014[2];
    }
  }
  if (in_stack_0000001c != (float *)0x0) {
    in_stack_00000004[0xc] = (float)in_stack_00000004[0xc] + *in_stack_0000001c;
    in_stack_00000004[0xd] = in_stack_0000001c[1] + (float)in_stack_00000004[0xd];
    in_stack_00000004[0xe] = in_stack_0000001c[2] + (float)in_stack_00000004[0xe];
  }
  return (int)in_stack_00000004;
}
