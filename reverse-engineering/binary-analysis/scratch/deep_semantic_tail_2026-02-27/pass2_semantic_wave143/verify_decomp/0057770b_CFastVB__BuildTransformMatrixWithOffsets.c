/* address: 0x0057770b */
/* name: CFastVB__BuildTransformMatrixWithOffsets */
/* signature: int CFastVB__BuildTransformMatrixWithOffsets(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CFastVB__BuildTransformMatrixWithOffsets(void)

{
  undefined4 *in_stack_00000004;
  undefined4 in_stack_00000008;
  float *in_stack_0000000c;
  int in_stack_00000010;
  float *in_stack_00000014;

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
  *in_stack_00000004 = in_stack_00000008;
  in_stack_00000004[5] = in_stack_00000008;
  in_stack_00000004[10] = in_stack_00000008;
  in_stack_00000004[0xf] = 0x3f800000;
  if (in_stack_00000010 != 0) {
    CTexture__Helper_005775bd();
    if (in_stack_0000000c == (float *)0x0) {
      CTexture__Helper_005768fe();
    }
    else {
      in_stack_00000004[0xc] = (float)in_stack_00000004[0xc] - *in_stack_0000000c;
      in_stack_00000004[0xd] = (float)in_stack_00000004[0xd] - in_stack_0000000c[1];
      in_stack_00000004[0xe] = (float)in_stack_00000004[0xe] - in_stack_0000000c[2];
      CTexture__Helper_005768fe();
      in_stack_00000004[0xc] = *in_stack_0000000c + (float)in_stack_00000004[0xc];
      in_stack_00000004[0xd] = (float)in_stack_00000004[0xd] + in_stack_0000000c[1];
      in_stack_00000004[0xe] = in_stack_0000000c[2] + (float)in_stack_00000004[0xe];
    }
  }
  if (in_stack_00000014 != (float *)0x0) {
    in_stack_00000004[0xc] = *in_stack_00000014 + (float)in_stack_00000004[0xc];
    in_stack_00000004[0xd] = in_stack_00000014[1] + (float)in_stack_00000004[0xd];
    in_stack_00000004[0xe] = in_stack_00000014[2] + (float)in_stack_00000004[0xe];
  }
  return (int)in_stack_00000004;
}
