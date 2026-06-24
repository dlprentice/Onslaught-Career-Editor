/* address: 0x0053d4c0 */
/* name: CDXEngine__UploadScaledRgbLookupTable */
/* signature: void __thiscall CDXEngine__UploadScaledRgbLookupTable(void * this, int param_1, float param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CDXEngine__UploadScaledRgbLookupTable(void *this,int param_1,float param_2)

{
  float fVar1;
  float fVar2;
  ushort *puVar3;
  ushort *puVar4;
  int iVar5;
  byte local_608;
  ushort local_600 [256];
  ushort local_400 [256];
  ushort local_200 [256];

  iVar5 = 0x100;
  puVar3 = (ushort *)((int)this + 0x6f4);
  puVar4 = local_400;
  do {
    fVar1 = (float)iVar5 * (float)param_1;
    fVar2 = _DAT_005d8568;
    if ((fVar1 <= _DAT_005d8568) && (fVar2 = fVar1, fVar1 < _DAT_005d856c)) {
      fVar2 = _DAT_005d856c;
    }
    fVar2 = _DAT_005d8568 - fVar2;
    local_608 = (byte)(longlong)ROUND((float)puVar3[-0x100] * fVar2);
    puVar4[-0x100] = (ushort)local_608;
    local_608 = (byte)(longlong)ROUND((float)*puVar3 * fVar2);
    *puVar4 = (ushort)local_608;
    local_608 = (byte)(longlong)ROUND((float)puVar3[0x100] * fVar2);
    puVar4[0x100] = (ushort)local_608;
    puVar4[-0x100] = puVar4[-0x100] * 0x101;
    *puVar4 = *puVar4 * 0x101;
    puVar4[0x100] = puVar4[0x100] * 0x101;
    iVar5 = iVar5 + -1;
    puVar3 = puVar3 + 1;
    puVar4 = puVar4 + 1;
  } while (0 < iVar5);
  (**(code **)(*DAT_00888a50 + 0x54))(DAT_00888a50,0,0,local_600);
  return;
}
