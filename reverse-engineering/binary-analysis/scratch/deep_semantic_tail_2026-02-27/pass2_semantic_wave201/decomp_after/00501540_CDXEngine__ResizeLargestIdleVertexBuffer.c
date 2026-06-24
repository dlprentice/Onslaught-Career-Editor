/* address: 0x00501540 */
/* name: CDXEngine__ResizeLargestIdleVertexBuffer */
/* signature: void CDXEngine__ResizeLargestIdleVertexBuffer(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CDXEngine__ResizeLargestIdleVertexBuffer(void)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;

  if (DAT_00633d2c == '\0') {
    iVar5 = 0;
    iVar3 = 0;
    iVar4 = DAT_00854e00;
    if (DAT_00854e00 != 0) {
      do {
        if (*(char *)(iVar4 + 0x5c) == '\0') {
          iVar2 = *(int *)(iVar4 + 0x1c);
          if (*(int *)(iVar4 + 0x1c) < *(int *)(iVar4 + 100)) {
            iVar2 = *(int *)(iVar4 + 100);
          }
          if (iVar2 == 0) {
            iVar7 = 0;
          }
          else {
            iVar7 = 0x400;
            if (0x400 < iVar2) {
              do {
                iVar7 = iVar7 * 2;
              } while (iVar7 < iVar2);
            }
          }
          iVar2 = *(int *)(iVar4 + 0x14 + *(int *)(iVar4 + 0x48) * 4);
          if (iVar7 < iVar2) {
            iVar6 = 0;
            do {
              iVar2 = iVar2 >> 1;
              iVar6 = iVar6 + 1;
            } while (iVar7 < iVar2);
            if (iVar5 < iVar6) {
              iVar3 = iVar4;
              iVar5 = iVar6;
            }
          }
        }
        piVar1 = (int *)(iVar4 + 0x58);
        iVar4 = *piVar1;
      } while (*piVar1 != 0);
      if (iVar3 != 0) {
        CVBufTexture__ResizeVertexBuffer(*(undefined4 *)(iVar3 + 100));
      }
    }
  }
  return;
}
