/* address: 0x00592a80 */
/* name: CDXTexture__InitJpegMarkerReader */
/* signature: void __stdcall CDXTexture__InitJpegMarkerReader(int param_1) */


void CDXTexture__InitJpegMarkerReader(int param_1)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  int iVar3;

  puVar1 = (undefined4 *)(*(code *)**(undefined4 **)(param_1 + 4))(param_1,0,0xac);
  *(undefined4 **)(param_1 + 0x1bc) = puVar1;
  *puVar1 = &LAB_00592a50;
  puVar1[1] = &LAB_005925c0;
  puVar1[2] = CDXTexture__ConsumeExpectedRestartMarker;
  puVar1[7] = CTexture__Helper_00592380;
  puVar1[0x18] = 0;
  puVar2 = puVar1 + 0x19;
  iVar3 = 0x10;
  do {
    puVar2[-0x11] = CTexture__Helper_00592380;
    *puVar2 = 0;
    puVar2 = puVar2 + 1;
    iVar3 = iVar3 + -1;
  } while (iVar3 != 0);
  puVar1[8] = &LAB_00592240;
  puVar1[0x16] = &LAB_00592240;
  *(undefined4 *)(param_1 + 0xdc) = 0;
  *(undefined4 *)(param_1 + 0x94) = 0;
  *(undefined4 *)(param_1 + 0x1a4) = 0;
  puVar1[3] = 0;
  puVar1[4] = 0;
  puVar1[6] = 0;
  puVar1[0x29] = 0;
  return;
}
