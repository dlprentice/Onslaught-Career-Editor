/* address: 0x005921a0 */
/* name: CDXTexture__Unk_005921a0 */
/* signature: void __thiscall CDXTexture__Unk_005921a0(void * this, uint param_1, int param_2) */


void __thiscall CDXTexture__Unk_005921a0(void *this,uint param_1,int param_2)

{
  byte bVar1;
  char cVar2;
  int iVar3;
  char *in_EAX;
  int *unaff_ESI;

  if (((((void *)0xb < this) && (*in_EAX == 'A')) && (in_EAX[1] == 'd')) &&
     (((in_EAX[2] == 'o' && (in_EAX[3] == 'b')) && (in_EAX[4] == 'e')))) {
    iVar3 = *unaff_ESI;
    bVar1 = in_EAX[0xb];
    cVar2 = in_EAX[8];
    *(uint *)(iVar3 + 0x18) = (uint)CONCAT11(in_EAX[5],in_EAX[6]);
    *(uint *)(iVar3 + 0x1c) = (uint)CONCAT11(in_EAX[7],cVar2);
    *(uint *)(iVar3 + 0x20) = (uint)CONCAT11(in_EAX[9],in_EAX[10]);
    *(uint *)(iVar3 + 0x24) = (uint)bVar1;
    *(undefined4 *)(iVar3 + 0x14) = 0x4c;
    (**(code **)(iVar3 + 4))();
    *(byte *)(unaff_ESI + 0x4b) = bVar1;
    unaff_ESI[0x4a] = 1;
    return;
  }
  iVar3 = *unaff_ESI;
  *(undefined4 *)(iVar3 + 0x14) = 0x4e;
  *(uint *)(iVar3 + 0x18) = (int)this + param_1;
  (**(code **)(iVar3 + 4))();
  return;
}
