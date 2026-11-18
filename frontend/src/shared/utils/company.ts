export const COMPANY_TYPES = [
  'Autónomo',
  'Sociedad limitada',
  'Sociedad anónima',
  'Cooperativa',
  'Asociación',
].map((value) => ({ value, label: value }))

export const COMPANY_ACTIVITIES = [
  'Comercio al por menor de libros',
  'Comercio al por menor de ropa',
  'Comercio al por menor de alimentación',
  'Hostelería y restauración',
  'Servicios profesionales',
  'Taller y reparaciones',
  'Salud y bienestar',
  'Ocio y cultura',
].map((value) => ({ value, label: value }))

export const PROVINCES = [
  'Álava', 'Albacete', 'Alicante', 'Almería', 'Asturias', 'Ávila', 'Badajoz', 'Barcelona',
  'Burgos', 'Cáceres', 'Cádiz', 'Cantabria', 'Castellón', 'Ceuta', 'Ciudad Real', 'Córdoba',
  'Cuenca', 'Girona', 'Granada', 'Guadalajara', 'Guipúzcoa', 'Huelva', 'Huesca', 'Islas Baleares',
  'Jaén', 'La Coruña', 'La Rioja', 'Las Palmas', 'León', 'Lleida', 'Lugo', 'Madrid', 'Málaga',
  'Melilla', 'Murcia', 'Navarra', 'Ourense', 'Palencia', 'Pontevedra', 'Salamanca',
  'Santa Cruz de Tenerife', 'Segovia', 'Sevilla', 'Soria', 'Tarragona', 'Teruel', 'Toledo',
  'Valencia', 'Valladolid', 'Vizcaya', 'Zamora', 'Zaragoza',
].map((value) => ({ value, label: value }))

export const COUNTRIES = [
  'España',
  'Portugal',
  'Francia',
  'Italia',
  'Alemania',
  'Reino Unido',
].map((value) => ({ value, label: value }))
