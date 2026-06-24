/* address: 0x00578a20 */
/* name: CDXTexture__Unk_00578a20 */
/* signature: int CDXTexture__Unk_00578a20(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CDXTexture__Unk_00578a20(void)

{
  float fVar1;
  float fVar2;
  float *in_stack_00000004;
  int *in_stack_0000000c;
  int in_stack_00000010;
  int in_stack_00000014;
  int in_stack_00000018;

  switch(((in_stack_00000018 != 0) << 1 | in_stack_00000014 != 0) << 1 | in_stack_00000010 != 0) {
  case '\0':
    break;
  case '\x01':
    break;
  case '\x02':
    break;
  case '\x03':
    goto LAB_00578af1;
  case '\x04':
    break;
  case '\x05':
    goto LAB_00578af1;
  case '\x06':
    goto LAB_00578af1;
  case '\a':
    CTexture__Helper_005768fe();
LAB_00578af1:
    CTexture__Helper_005768fe();
  }
  CDXEngine__Helper_00576161();
  if (in_stack_0000000c != (int *)0x0) {
    fVar2 = (float)in_stack_0000000c[2];
    if (in_stack_0000000c[2] < 0) {
      fVar2 = fVar2 + _DAT_005e72d8;
    }
    fVar1 = (float)*in_stack_0000000c;
    if (*in_stack_0000000c < 0) {
      fVar1 = fVar1 + _DAT_005e72d8;
    }
    *in_stack_00000004 = fVar1 + fVar2 * (*in_stack_00000004 + _DAT_005e6a34) * _DAT_005e72d4;
    fVar2 = (float)in_stack_0000000c[3];
    if (in_stack_0000000c[3] < 0) {
      fVar2 = fVar2 + _DAT_005e72d8;
    }
    fVar1 = (float)in_stack_0000000c[1];
    if (in_stack_0000000c[1] < 0) {
      fVar1 = fVar1 + _DAT_005e72d8;
    }
    in_stack_00000004[1] = fVar1 + fVar2 * (1.0 - in_stack_00000004[1]) * _DAT_005e72d4;
    in_stack_00000004[2] =
         ((float)in_stack_0000000c[5] - (float)in_stack_0000000c[4]) * in_stack_00000004[2] +
         (float)in_stack_0000000c[4];
  }
  return (int)in_stack_00000004;
}
