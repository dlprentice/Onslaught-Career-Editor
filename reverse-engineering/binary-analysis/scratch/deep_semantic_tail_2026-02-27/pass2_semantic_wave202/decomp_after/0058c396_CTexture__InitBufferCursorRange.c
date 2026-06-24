/* address: 0x0058c396 */
/* name: CTexture__InitBufferCursorRange */
/* signature: int CTexture__InitBufferCursorRange(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CTexture__InitBufferCursorRange(void)

{
  char cVar1;
  char *pcVar2;
  undefined4 *in_ECX;
  char *in_stack_00000004;
  int in_stack_00000008;
  undefined4 in_stack_0000000c;
  undefined4 in_stack_00000010;
  int in_stack_00000014;
  int in_stack_00000018;

  if ((in_stack_00000014 != 0) && (in_stack_00000018 != 0)) {
    if (in_stack_00000008 == -1) {
      if (in_stack_00000004 == (char *)0x0) {
        in_stack_00000008 = 0;
      }
      else {
        pcVar2 = in_stack_00000004;
        do {
          cVar1 = *pcVar2;
          pcVar2 = pcVar2 + 1;
        } while (cVar1 != '\0');
        in_stack_00000008 = (int)pcVar2 - (int)(in_stack_00000004 + 1);
      }
    }
    if ((in_stack_00000004 != (char *)0x0) || (in_stack_00000008 == 0)) {
      *in_ECX = in_stack_00000004;
      in_ECX[6] = in_stack_0000000c;
      in_ECX[7] = in_stack_00000010;
      in_ECX[0xb] = in_stack_00000014;
      in_ECX[1] = in_stack_00000004 + in_stack_00000008;
      in_ECX[0xc] = in_stack_00000018;
      return 0;
    }
  }
  return -0x7fffbffb;
}
