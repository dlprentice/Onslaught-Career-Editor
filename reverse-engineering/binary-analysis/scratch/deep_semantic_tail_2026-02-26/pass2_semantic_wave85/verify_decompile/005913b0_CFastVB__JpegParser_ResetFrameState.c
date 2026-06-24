/* address: 0x005913b0 */
/* name: CFastVB__JpegParser_ResetFrameState */
/* signature: int CFastVB__JpegParser_ResetFrameState(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CFastVB__JpegParser_ResetFrameState(void)

{
  undefined4 *puVar1;
  int *piVar2;
  int iVar3;
  int *unaff_ESI;

  iVar3 = *unaff_ESI;
  *(undefined4 *)(iVar3 + 0x14) = 0x66;
  (**(code **)(iVar3 + 4))();
  if (*(int *)(unaff_ESI[0x6f] + 0xc) != 0) {
    puVar1 = (undefined4 *)*unaff_ESI;
    puVar1[5] = 0x3d;
    (*(code *)*puVar1)();
  }
  piVar2 = unaff_ESI + 0x3e;
  iVar3 = 0x10;
  do {
    *(undefined1 *)(piVar2 + -4) = 0;
    *(undefined1 *)piVar2 = 1;
    *(undefined1 *)(piVar2 + 4) = 5;
    piVar2 = (int *)((int)piVar2 + 1);
    iVar3 = iVar3 + -1;
  } while (iVar3 != 0);
  unaff_ESI[0x46] = 0;
  unaff_ESI[10] = 0;
  unaff_ESI[0x4c] = 0;
  unaff_ESI[0x47] = 0;
  *(undefined1 *)((int)unaff_ESI + 0x122) = 0;
  unaff_ESI[0x4a] = 0;
  *(undefined1 *)(unaff_ESI + 0x4b) = 0;
  *(undefined1 *)(unaff_ESI + 0x48) = 1;
  *(undefined1 *)((int)unaff_ESI + 0x121) = 1;
  *(undefined2 *)(unaff_ESI + 0x49) = 1;
  *(undefined2 *)((int)unaff_ESI + 0x126) = 1;
  *(undefined4 *)(unaff_ESI[0x6f] + 0xc) = 1;
  return 1;
}
