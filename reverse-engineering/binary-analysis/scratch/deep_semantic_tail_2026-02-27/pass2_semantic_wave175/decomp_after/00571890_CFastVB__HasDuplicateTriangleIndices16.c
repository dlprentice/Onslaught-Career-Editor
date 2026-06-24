/* address: 0x00571890 */
/* name: CFastVB__HasDuplicateTriangleIndices16 */
/* signature: bool __stdcall CFastVB__HasDuplicateTriangleIndices16(int param_1, int param_2, int param_3) */


bool CFastVB__HasDuplicateTriangleIndices16(int param_1,int param_2,int param_3)

{
  if ((short)param_1 == (short)param_2) {
    return true;
  }
  if ((short)param_1 == (short)param_3) {
    return true;
  }
  return (short)param_2 == (short)param_3;
}
