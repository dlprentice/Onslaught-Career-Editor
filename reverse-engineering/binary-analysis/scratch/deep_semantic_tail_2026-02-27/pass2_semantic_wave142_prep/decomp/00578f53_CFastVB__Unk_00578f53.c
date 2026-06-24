/* address: 0x00578f53 */
/* name: CFastVB__Unk_00578f53 */
/* signature: void CFastVB__Unk_00578f53(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CFastVB__Unk_00578f53(void)

{
  int in_stack_00000014;
  int in_stack_00000018;
  int in_stack_0000001c;
  int in_stack_00000020;

  switch(((in_stack_00000020 != 0) << 1 | in_stack_0000001c != 0) << 1 | in_stack_00000018 != 0) {
  case '\0':
    goto switchD_00578f93_default;
  case '\x01':
    goto LAB_00579031;
  case '\x02':
    goto LAB_00579031;
  case '\x03':
    break;
  case '\x04':
    goto LAB_00579031;
  case '\x05':
    break;
  case '\x06':
    break;
  case '\a':
    CTexture__Helper_005768fe();
    break;
  default:
    goto switchD_00578f93_default;
  }
  CTexture__Helper_005768fe();
LAB_00579031:
  CVertexShader__Helper_00576e0a();
switchD_00578f93_default:
  if (in_stack_00000014 != 0) {
    CTexture__Helper_005768fe();
  }
  CTexture__Unk_00576178();
  return;
}
