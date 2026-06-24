/* address: 0x004f6fd0 */
/* name: CUnit__RenderWithDistanceFade */
/* signature: int __thiscall CUnit__RenderWithDistanceFade(void * this, void * param_1, int param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __thiscall CUnit__RenderWithDistanceFade(void *this,void *param_1,int param_2)

{
  float fVar1;
  undefined4 in_EAX;
  undefined4 extraout_EAX;

  fVar1 = *(float *)(*(int *)((int)this + 0x48) + 0xbc);
  if (fVar1 >= _DAT_005d856c && (fVar1 == _DAT_005d856c) == 0) {
    fVar1 = (*(float *)(*(int *)((int)this + 0x48) + 0xbc) + _DAT_005d85d8) - DAT_00672fd0;
    if (fVar1 < _DAT_005d856c) {
      fVar1 = _DAT_005d856c;
    }
    DAT_0063012c = (uint)(longlong)ROUND(fVar1 * _DAT_005d8c68 * _DAT_005d8c70);
    CThing__Render(this,(int)param_1,DAT_0063012c);
    DAT_0063012c = 0xff;
    return CONCAT31((int3)((uint)extraout_EAX >> 8),1);
  }
  return CONCAT22((short)((uint)in_EAX >> 0x10),
                  (ushort)(fVar1 < _DAT_005d856c) << 8 |
                  (ushort)(NAN(fVar1) || NAN(_DAT_005d856c)) << 10 |
                  (ushort)(fVar1 == _DAT_005d856c) << 0xe);
}
