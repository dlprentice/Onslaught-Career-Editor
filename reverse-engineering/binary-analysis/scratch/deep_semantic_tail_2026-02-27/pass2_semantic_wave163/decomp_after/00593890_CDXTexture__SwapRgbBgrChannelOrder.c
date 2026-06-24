/* address: 0x00593890 */
/* name: CDXTexture__SwapRgbBgrChannelOrder */
/* signature: void __stdcall CDXTexture__SwapRgbBgrChannelOrder(void * param_1, void * param_2) */


void CDXTexture__SwapRgbBgrChannelOrder(void *param_1,void *param_2)

{
  byte bVar1;
  undefined1 uVar2;
  undefined1 *puVar3;
  int iVar4;

  bVar1 = *(byte *)((int)param_1 + 8);
  if ((bVar1 & 2) != 0) {
    iVar4 = *(int *)param_1;
    if (*(char *)((int)param_1 + 9) == '\b') {
      if (bVar1 == 2) {
        for (; iVar4 != 0; iVar4 = iVar4 + -1) {
          uVar2 = *(undefined1 *)param_2;
          *(undefined1 *)param_2 = *(undefined1 *)((int)param_2 + 2);
          *(undefined1 *)((int)param_2 + 2) = uVar2;
          param_2 = (void *)((int)param_2 + 3);
        }
      }
      else if (bVar1 == 6) {
        for (; iVar4 != 0; iVar4 = iVar4 + -1) {
          uVar2 = *(undefined1 *)param_2;
          *(undefined1 *)param_2 = *(undefined1 *)((int)param_2 + 2);
          *(undefined1 *)((int)param_2 + 2) = uVar2;
          param_2 = (void *)((int)param_2 + 4);
        }
      }
    }
    else if (*(char *)((int)param_1 + 9) == '\x10') {
      if (bVar1 == 2) {
        if (iVar4 != 0) {
          puVar3 = (undefined1 *)((int)param_2 + 1);
          do {
            uVar2 = puVar3[-1];
            puVar3[-1] = puVar3[3];
            puVar3[3] = uVar2;
            uVar2 = *puVar3;
            *puVar3 = puVar3[4];
            puVar3[4] = uVar2;
            puVar3 = puVar3 + 6;
            iVar4 = iVar4 + -1;
          } while (iVar4 != 0);
        }
      }
      else if ((bVar1 == 6) && (iVar4 != 0)) {
        puVar3 = (undefined1 *)((int)param_2 + 1);
        do {
          uVar2 = puVar3[-1];
          puVar3[-1] = puVar3[3];
          puVar3[3] = uVar2;
          uVar2 = *puVar3;
          *puVar3 = puVar3[4];
          puVar3[4] = uVar2;
          puVar3 = puVar3 + 8;
          iVar4 = iVar4 + -1;
        } while (iVar4 != 0);
      }
    }
  }
  return;
}
