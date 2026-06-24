/* address: 0x00578dad */
/* name: CTexture__Unk_00578dad */
/* signature: int CTexture__Unk_00578dad(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CTexture__Unk_00578dad(void)

{
  float fVar1;
  float fVar2;
  float *in_stack_00000004;
  float *in_stack_00000008;
  int *in_stack_0000000c;
  int in_stack_00000010;
  int in_stack_00000014;
  int in_stack_00000018;

  switch(((in_stack_00000018 != 0) << 1 | in_stack_00000014 != 0) << 1 | in_stack_00000010 != 0) {
  case '\0':
    goto switchD_00578dea_default;
  case '\x01':
    goto LAB_00578e88;
  case '\x02':
    goto LAB_00578e88;
  case '\x03':
    break;
  case '\x04':
    goto LAB_00578e88;
  case '\x05':
    break;
  case '\x06':
    break;
  case '\a':
    CTexture__Helper_005768fe();
    break;
  default:
    goto switchD_00578dea_default;
  }
  CTexture__Helper_005768fe();
LAB_00578e88:
  CVertexShader__Helper_00576e0a();
switchD_00578dea_default:
  if (in_stack_0000000c != (int *)0x0) {
    fVar1 = (float)*in_stack_0000000c;
    if (*in_stack_0000000c < 0) {
      fVar1 = fVar1 + _DAT_005e72d8;
    }
    fVar2 = (float)in_stack_0000000c[2];
    if (in_stack_0000000c[2] < 0) {
      fVar2 = fVar2 + _DAT_005e72d8;
    }
    fVar2 = (*in_stack_00000008 - fVar1) / fVar2;
    *in_stack_00000004 = (fVar2 + fVar2) - _DAT_005e6a34;
    fVar1 = (float)in_stack_0000000c[1];
    if (in_stack_0000000c[1] < 0) {
      fVar1 = fVar1 + _DAT_005e72d8;
    }
    fVar2 = (float)in_stack_0000000c[3];
    if (in_stack_0000000c[3] < 0) {
      fVar2 = fVar2 + _DAT_005e72d8;
    }
    fVar2 = (in_stack_00000008[1] - fVar1) / fVar2;
    in_stack_00000004[1] = -((fVar2 + fVar2) - _DAT_005e6a34);
    in_stack_00000004[2] =
         (in_stack_00000008[2] - (float)in_stack_0000000c[4]) /
         ((float)in_stack_0000000c[5] - (float)in_stack_0000000c[4]);
  }
  CDXEngine__Helper_00576161();
  return (int)in_stack_00000004;
}
