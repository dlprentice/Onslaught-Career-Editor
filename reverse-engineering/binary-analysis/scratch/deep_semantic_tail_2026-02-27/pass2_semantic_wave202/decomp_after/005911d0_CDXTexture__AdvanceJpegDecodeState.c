/* address: 0x005911d0 */
/* name: CDXTexture__AdvanceJpegDecodeState */
/* signature: int __stdcall CDXTexture__AdvanceJpegDecodeState(void * param_1) */


int CDXTexture__AdvanceJpegDecodeState(void *param_1)

{
  undefined4 uVar1;
  undefined4 *puVar2;
  int iVar3;

  uVar1 = *(undefined4 *)((int)param_1 + 0x14);
  iVar3 = 0;
  switch(uVar1) {
  case 200:
    (**(code **)(*(int *)((int)param_1 + 0x1b8) + 4))(param_1);
    (**(code **)(*(int *)((int)param_1 + 0x18) + 8))(param_1);
    *(undefined4 *)((int)param_1 + 0x14) = 0xc9;
  case 0xc9:
    iVar3 = (*(code *)**(undefined4 **)((int)param_1 + 0x1b8))(param_1);
    if (iVar3 == 1) {
      CDXTexture__SelectJpegOutputDefaults();
      *(undefined4 *)((int)param_1 + 0x14) = 0xca;
      return 1;
    }
    break;
  case 0xca:
    return 1;
  case 0xcb:
  case 0xcc:
  case 0xcd:
  case 0xce:
  case 0xcf:
  case 0xd0:
  case 0xd2:
    iVar3 = (*(code *)**(undefined4 **)((int)param_1 + 0x1b8))(param_1);
    return iVar3;
  default:
    puVar2 = *(undefined4 **)param_1;
    puVar2[5] = 0x14;
    puVar2[6] = uVar1;
    (*(code *)*puVar2)(param_1);
  }
  return iVar3;
}
