/* address: 0x004c0940 */
/* name: CPDSimpleSprite__SetUVFromTileIndex */
/* signature: void __thiscall CPDSimpleSprite__SetUVFromTileIndex(void * this, int param_1, uint param_2, int param_3) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CPDSimpleSprite__SetUVFromTileIndex(void *this,int param_1,uint param_2,int param_3)

{
  float fVar1;
  float fVar2;
  float fVar3;
  byte bVar4;

  switch(param_2) {
  case 0:
    param_2 = 0x10;
    bVar4 = 4;
    break;
  case 1:
    param_2 = 8;
    bVar4 = 3;
    break;
  case 2:
    param_2 = 4;
    bVar4 = 2;
    break;
  case 3:
    param_2 = 2;
    bVar4 = 1;
    break;
  case 4:
    param_2 = 1;
    bVar4 = 0;
    break;
  default:
    bVar4 = (byte)param_2;
  }
  if ((*(int *)((int)this + 0x6c) != 0) && (*(int *)((int)this + 0x8c) != -1)) {
    fVar2 = (float)(int)param_2;
    fVar1 = (float)(int)(param_2 - 1 & param_1) / fVar2;
    *(float *)((int)this + 0xb8) = fVar1;
    fVar3 = (float)(param_1 >> (bVar4 & 0x1f)) / fVar2;
    *(float *)((int)this + 0xbc) = fVar3;
    fVar2 = _DAT_005d8568 / fVar2;
    *(float *)((int)this + 0xc0) = fVar2 + fVar1;
    *(float *)((int)this + 0xc4) = fVar2 + fVar3;
    return;
  }
  *(undefined4 *)((int)this + 0xbc) = 0;
  *(undefined4 *)((int)this + 0xb8) = 0;
  *(undefined4 *)((int)this + 0xc4) = 0x3f800000;
  *(undefined4 *)((int)this + 0xc0) = 0x3f800000;
  return;
}
