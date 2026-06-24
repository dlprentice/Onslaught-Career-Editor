/* address: 0x0058d821 */
/* name: CTexture__Helper_0058d821 */
/* signature: int CTexture__Helper_0058d821(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CTexture__Helper_0058d821(void)

{
  short in_stack_0000000c;
  int in_stack_00000010;
  undefined4 *in_stack_00000018;

  if (in_stack_0000000c == 1) {
LAB_0058d866:
    CTexture__Helper_0058c95c
              ((void *)*in_stack_00000018,in_stack_00000018[0xc],in_stack_00000010 + 5000);
  }
  else {
    if (in_stack_0000000c != 2) {
      if (in_stack_0000000c == 5) goto LAB_0058d866;
      if (in_stack_0000000c != 6) {
        return 0;
      }
    }
    CTexture__Helper_0058c893
              ((void *)*in_stack_00000018,in_stack_00000018[0xc],in_stack_00000010 + 5000,0x5ea38c);
    in_stack_00000018[0x13] = 1;
  }
  return 0;
}
