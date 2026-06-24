/* address: 0x0053bda0 */
/* name: CHud__Helper_0053bda0 */
/* signature: void __fastcall CHud__Helper_0053bda0(int param_1) */


void __fastcall CHud__Helper_0053bda0(int param_1)

{
  void *obj;
  int iVar1;
  int *piVar2;

  iVar1 = 2;
  piVar2 = (int *)(param_1 + 0x3f04);
  do {
    if (piVar2[-0xc1] != 0) {
      CHud__Helper_004f27e0(piVar2[-0xc1] + 8);
      piVar2[-0xc1] = 0;
    }
    if (*piVar2 != 0) {
      CHud__Helper_004f27e0(*piVar2 + 8);
      *piVar2 = 0;
    }
    piVar2 = piVar2 + 1;
    iVar1 = iVar1 + -1;
  } while (iVar1 != 0);
  if (*(undefined4 **)(param_1 + 0x3f0c) != (undefined4 *)0x0) {
    (**(code **)**(undefined4 **)(param_1 + 0x3f0c))(1);
    *(undefined4 *)(param_1 + 0x3f0c) = 0;
  }
  obj = *(void **)(param_1 + 0x3c08);
  if (obj != (void *)0x0) {
    CByteSprite__Free();
    OID__FreeObject(obj);
    *(undefined4 *)(param_1 + 0x3c08) = 0;
  }
  if (*(undefined4 **)(param_1 + 0x3f10) != (undefined4 *)0x0) {
    (**(code **)**(undefined4 **)(param_1 + 0x3f10))(1);
    *(undefined4 *)(param_1 + 0x3f10) = 0;
  }
  return;
}
