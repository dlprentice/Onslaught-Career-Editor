/* address: 0x00562ad6 */
/* name: CTexture__Helper_00562ad6 */
/* signature: int __cdecl CTexture__Helper_00562ad6(int param_1) */


int __cdecl CTexture__Helper_00562ad6(int param_1)

{
  undefined4 uStack_4;

  if ((param_1 & 0x20U) == 0) {
    if ((param_1 & 8U) == 0) {
      if ((param_1 & 4U) == 0) {
        if ((param_1 & 1U) == 0) {
          return (param_1 & 2U) << 1;
        }
        uStack_4 = 3;
      }
      else {
        uStack_4 = 2;
      }
    }
    else {
      uStack_4 = 1;
    }
  }
  else {
    uStack_4 = 5;
  }
  return uStack_4;
}
